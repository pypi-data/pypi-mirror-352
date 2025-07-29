import json
import orjson
import pandas as pd
import polars as pl
import pyarrow.parquet as pq
import tarfile
import io
import requests
import tarfile
from zipfile import ZipFile, ZipInfo

from prismstudio._utils.exceptions import PrismAuthError, PrismError, PrismResponseError
from .auth_utils import _authentication
from .._common.config import *
from .._common.const import *


def _process_response(res, content=None):
    if res.status_code >= 400:
        if res.status_code == 401:
            raise PrismAuthError(f"Please Login First")

        if res.status_code == 422:
            arg = res.json()["detail"][0]["loc"][-1]
            # enum_list = res.json()["detail"][0]["ctx"]["enum_values"]
            raise PrismResponseError(f'Value at "{arg}" is not a valid enumeration member')

        try:
            err_msg = res.json()["message"]
        except Exception as e:
            if content:
                err_msg = content
            else:
                err_msg = res.content
        raise PrismResponseError(err_msg)
    result = None
    if content:
        resjson = orjson.loads(content)
    else:
        resjson = orjson.loads(res.content)
    restype = resjson["restype"]
    rescontent = resjson["rescontent"]
    if restype == "status":
        result = rescontent
    else:
        data = rescontent.get("data")
        if data is not None:
            if isinstance(data, dict):
                if ("columns" in data.keys()) and (("data" in data.keys())):
                    cols = data.get("columns")
                    data = data.get("data")
                    datecolumns = []
                    cols_to_use = []
                    for c in cols:
                        if c["dtype"].startswith("datetime64"):
                            datecolumns.append(c["column"])
                        cols_to_use.append(c["column"])
                    result = pd.DataFrame(data, columns=cols_to_use)
                    for c in datecolumns:
                        result[c] = pd.to_datetime(result[c], unit="ns")
                else:
                    result = data
            else:
                result = data
        else:
            result = rescontent
    return result


def unzip_tar(content, data_type):
    dfs = {}
    tar_obj = tarfile.open(fileobj=io.BytesIO(content), mode='r')
    fname = tar_obj.getnames()
    metadata = None
    if fname is None: fname = []
    for name in fname:
        f = tar_obj.extractfile(name).read()
        if ".txt" in name:
            metadata = json.loads(f)
        else:
            if data_type=='pandas':
                obj = pq.read_table(io.BytesIO(f))
                dfs[name] = obj.to_pandas()
            elif data_type=='polars':
                dfs[name] = pl.read_parquet(io.BytesIO(f))
            else:
                raise ValueError(f'Invalid data_type: {data_type}')

    return dfs, metadata


def unzip_zip(content, data_type):
    dfs = {}
    zip_obj = ZipFile(io.BytesIO(content), mode='r')
    fname = zip_obj.filelist
    if fname is None: fname = []
    metadata = None
    for name in fname:
        f = zip_obj.read(name)
        if ".txt" in name.filename:
            metadata = json.loads(f)
        else:
            if data_type == 'pandas':
                obj = pq.read_table(io.BytesIO(f))
                dfs[name.filename] = obj.to_pandas()
            elif data_type=='polars':
                dfs[name] = pl.read_parquet(io.BytesIO(f))
            else:
                raise ValueError(f'Invalid data_type: {data_type}')
    return dfs, metadata


def _process_fileresponse(res, content=None, file_type='tar', data_type='pandas'):
    if res.status_code >= 400:
        try:
            err_msg = res.json()["message"]
        except:
            err_msg = res.content
        raise PrismError(err_msg)
    try:
        if file_type=='tar':
            fn = unzip_tar
        elif file_type=='zip':
            fn = unzip_zip
        else:
            raise ValueError(f'Invalid zip_file_type: {file_type}')
        return fn(content, data_type)
    except Exception as e:
        raise PrismError("Extension response processing error")


def get(url, params=None, stream=False):
    headers = _authentication()
    res = requests.get(url=url, params=params, headers=headers, stream=stream)
    return _process_response(res)


def post(url, params, body, stream=False):
    headers = _authentication()
    res = requests.post(url=url, params=params, json=body, headers=headers, stream=stream)
    return _process_response(res)


def patch(url, params, body):
    headers = _authentication()
    res = requests.patch(url=url, params=params, json=body, headers=headers)
    return _process_response(res)


def delete(url, params=None):
    headers = _authentication()
    res = requests.delete(url=url, params=params, headers=headers)
    return _process_response(res)


def _fetch_and_parse(url, ext, search=None):
    df = get(url, {"search": search})
    if not df.empty:
        directorytype = FILEEXTENSION[ext]
        df["path"] = df["path"].str.split("/", expand=True).replace({None:""}).iloc[:,2:].agg("/".join, axis=1)
        df["path"] = df["path"].str.split("." + ext, expand=True).iloc[:, 0]
        df = df.rename(columns={"path": directorytype + "name"})
        typeid = directorytype + "id"
        if ext == 'ped':
            setattr(df, typeid, getattr(df, typeid).astype('str'))
        else:
            setattr(df, typeid, getattr(df, typeid).astype('Int64'))
    return df[df['folderflag'] == 0].drop("folderflag", axis=1)
