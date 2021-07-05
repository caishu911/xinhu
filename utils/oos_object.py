import oos
from ooscore.client import Config
from oos.DomainConfig import *
from ooscore.exceptions import *
# import json
# import datetime
import ooscore.exceptions as exceptions
import traceback

class PoiObject:
    # 6.0 Server
    __ACCESS_KEY = '354afcdf7693df85dc5f'                                     # your id
    __SECRET_KEY = '7167f024d4791dac4a0713dbe9687b6b58b5ea16'                 # your key
    __ENDPOINT = 'http://oos-cn.ctyunapi.cn'                                  #
    __IAM_ENDPOINT = 'http://oos-cn-iam.ctyunapi.cn'                          # your domain
    __SIGNATURE_VERSION = 's3v4'                                              # signer version V4 's3v4'
    # SIGNATURE_VERSION = 's3'                                              # signer version V2 's3'
    __SERVICE_NAME = 's3'
    __IAM_SERVICE_NAME = 'sts'

    __BUCKET = 'hudx-poi-oos'
    KEY = ''
    # MULTIPART_UPLOAD_KEY = 'test-multi'
    UPLOAD_FILE = ''
    # DOWNLOAD_FILE_PATH = './foo'
    __API_VERSION = '2006-03-01'
    if __ENDPOINT.lower().find("http") < 0 and __ENDPOINT.lower().find("https") < 0:
        __ENDPOINT = "http://" + __ENDPOINT

    if __IAM_ENDPOINT.lower().find("http") < 0 and __IAM_ENDPOINT.lower().find("https") < 0:
        __IAM_ENDPOINT = "http://" + __IAM_ENDPOINT
    try:
        _config = Config(endpoint_url=__ENDPOINT, signature_version=__SIGNATURE_VERSION,
                        s3={'payload_signing_enabled': True})

        _iam_config = Config(endpoint_url=__IAM_ENDPOINT, signature_version=__SIGNATURE_VERSION,
                            s3={'payload_signing_enabled': True})

        client = oos.client(service_name=__SERVICE_NAME, use_ssl=False, endpoint_url=__ENDPOINT, api_version=__API_VERSION,
                            access_key_id=__ACCESS_KEY, secret_access_key=__SECRET_KEY,
                            config=_config)

        iam_client = oos.client(service_name=__IAM_SERVICE_NAME, use_ssl=False, endpoint_url=__IAM_ENDPOINT,
                                access_key_id=__ACCESS_KEY, secret_access_key=__SECRET_KEY,
                                config=_iam_config)
    except Exception as ex:
        # print(traceback.format_exc())
        # print(ex)
        exit(-1)

    def handle_error(fn):
        def inner(self):
            try:
                fn(self)
            except exceptions.ClientError as e:
                print('\n Response code: {0}\n Error message: {1}\n Resource: {2}\n request id: {3}'
                    .format(e.response['Error']['Code'],
                            e.response['Error']['Message'],
                            e.response['Error']['Resource'],
                            e.response['ResponseMetadata']['RequestId']
                            ))
        return inner
    # Object: 4.3.1 Put Object
    # 上传本地文件到OOS bucket，本例子适用于所有资源池
    @handle_error
    def put_image(self):
        ret = self.client.put_object(
            Bucket=self.__BUCKET,
            Key=self.KEY,
            Body=self.UPLOAD_FILE,
            StorageClass='STANDARD'           # STANDARD | REDUCED_REDUNDANCY | EC_N_M
        )
        return(ret)

    # @handle_error
    def generate_shared_link(self):
        shared_link = self.client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.__BUCKET,
                'Key': self.KEY
            },
            ExpiresIn=3600      # 过期时间
        )
        return(shared_link)