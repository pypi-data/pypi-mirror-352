from .ethz_iam import ETH_IAM

name = "ethz_iam_webservice"
__author__ = "Swen Vermeul"
__email__ = "swen@ethz.ch"
__version__ = "0.14.0"


def login(username, password):
    return ETH_IAM(admin_username=username, admin_password=password)
