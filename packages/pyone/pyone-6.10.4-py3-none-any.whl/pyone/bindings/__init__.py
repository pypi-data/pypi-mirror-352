#!/usr/bin/env python

#
# Generated Thu May 29 01:07:37 2025 by generateDS.py version 2.44.3.
# Python 3.10.12 (main, Feb  4 2025, 14:57:36) [GCC 11.4.0]
#
# Command line options:
#   ('-q', '')
#   ('-f', '')
#   ('-o', 'pyone/bindings/supbind.py')
#   ('-s', 'pyone/bindings/__init__.py')
#   ('--super', 'supbind')
#   ('--external-encoding', 'utf-8')
#   ('--silence', '')
#
# Command line arguments:
#   ../../../share/doc/xsd/index.xsd
#
# Command line:
#   /home/one/init-build-jenkins.p7F3uQ/one/src/oca/python/bin/generateDS -q -f -o "pyone/bindings/supbind.py" -s "pyone/bindings/__init__.py" --super="supbind" --external-encoding="utf-8" --silence ../../../share/doc/xsd/index.xsd
#
# Current working directory (os.getcwd()):
#   python
#

import os
import sys
from pyone.util import TemplatedType
from lxml import etree as etree_

from . import supbind as supermod

def parsexml_(infile, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        parser = etree_.ETCompatXMLParser()
    try:
        if isinstance(infile, os.PathLike):
            infile = os.path.join(infile)
    except AttributeError:
        pass
    doc = etree_.parse(infile, parser=parser, **kwargs)
    return doc

def parsexmlstring_(instring, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        try:
            parser = etree_.ETCompatXMLParser()
        except AttributeError:
            # fallback to xml.etree
            parser = etree_.XMLParser()
    element = etree_.fromstring(instring, parser=parser, **kwargs)
    return element

#
# Globals
#

ExternalEncoding = 'utf-8'
SaveElementTreeNode = True

#
# Data representation classes
#


class HISTORY_RECORDSSub(TemplatedType, supermod.HISTORY_RECORDS):
    def __init__(self, HISTORY=None, **kwargs_):
        super(HISTORY_RECORDSSub, self).__init__(HISTORY,  **kwargs_)
supermod.HISTORY_RECORDS.subclass = HISTORY_RECORDSSub
# end class HISTORY_RECORDSSub


class HISTORYSub(TemplatedType, supermod.HISTORY):
    def __init__(self, OID=None, SEQ=None, HOSTNAME=None, HID=None, CID=None, STIME=None, ETIME=None, VM_MAD=None, TM_MAD=None, DS_ID=None, PSTIME=None, PETIME=None, RSTIME=None, RETIME=None, ESTIME=None, EETIME=None, ACTION=None, UID=None, GID=None, REQUEST_ID=None, VM=None, **kwargs_):
        super(HISTORYSub, self).__init__(OID, SEQ, HOSTNAME, HID, CID, STIME, ETIME, VM_MAD, TM_MAD, DS_ID, PSTIME, PETIME, RSTIME, RETIME, ESTIME, EETIME, ACTION, UID, GID, REQUEST_ID, VM,  **kwargs_)
supermod.HISTORY.subclass = HISTORYSub
# end class HISTORYSub


class ACL_POOLSub(TemplatedType, supermod.ACL_POOL):
    def __init__(self, ACL=None, **kwargs_):
        super(ACL_POOLSub, self).__init__(ACL,  **kwargs_)
supermod.ACL_POOL.subclass = ACL_POOLSub
# end class ACL_POOLSub


class CALL_INFOSub(TemplatedType, supermod.CALL_INFO):
    def __init__(self, RESULT=None, PARAMETERS=None, EXTRA=None, **kwargs_):
        super(CALL_INFOSub, self).__init__(RESULT, PARAMETERS, EXTRA,  **kwargs_)
supermod.CALL_INFO.subclass = CALL_INFOSub
# end class CALL_INFOSub


class BACKUPJOB_POOLSub(TemplatedType, supermod.BACKUPJOB_POOL):
    def __init__(self, BACKUPJOB=None, **kwargs_):
        super(BACKUPJOB_POOLSub, self).__init__(BACKUPJOB,  **kwargs_)
supermod.BACKUPJOB_POOL.subclass = BACKUPJOB_POOLSub
# end class BACKUPJOB_POOLSub


class BACKUPJOBSub(TemplatedType, supermod.BACKUPJOB):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LOCK=None, PERMISSIONS=None, PRIORITY=None, LAST_BACKUP_TIME=None, LAST_BACKUP_DURATION=None, SCHED_ACTIONS=None, UPDATED_VMS=None, OUTDATED_VMS=None, BACKING_UP_VMS=None, ERROR_VMS=None, TEMPLATE=None, **kwargs_):
        super(BACKUPJOBSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LOCK, PERMISSIONS, PRIORITY, LAST_BACKUP_TIME, LAST_BACKUP_DURATION, SCHED_ACTIONS, UPDATED_VMS, OUTDATED_VMS, BACKING_UP_VMS, ERROR_VMS, TEMPLATE,  **kwargs_)
supermod.BACKUPJOB.subclass = BACKUPJOBSub
# end class BACKUPJOBSub


class LOCKSub(TemplatedType, supermod.LOCK):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKSub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCK.subclass = LOCKSub
# end class LOCKSub


class PERMISSIONSSub(TemplatedType, supermod.PERMISSIONS):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSSub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONS.subclass = PERMISSIONSSub
# end class PERMISSIONSSub


class IDSSub(TemplatedType, supermod.IDS):
    def __init__(self, ID=None, **kwargs_):
        super(IDSSub, self).__init__(ID,  **kwargs_)
supermod.IDS.subclass = IDSSub
# end class IDSSub


class SCHED_ACTIONSub(TemplatedType, supermod.SCHED_ACTION):
    def __init__(self, ID=None, PARENT_ID=None, TYPE=None, ACTION=None, ARGS=None, TIME=None, REPEAT=None, DAYS=None, END_TYPE=None, END_VALUE=None, DONE=None, MESSAGE=None, WARNING=None, **kwargs_):
        super(SCHED_ACTIONSub, self).__init__(ID, PARENT_ID, TYPE, ACTION, ARGS, TIME, REPEAT, DAYS, END_TYPE, END_VALUE, DONE, MESSAGE, WARNING,  **kwargs_)
supermod.SCHED_ACTION.subclass = SCHED_ACTIONSub
# end class SCHED_ACTIONSub


class CLUSTER_POOLSub(TemplatedType, supermod.CLUSTER_POOL):
    def __init__(self, CLUSTER=None, **kwargs_):
        super(CLUSTER_POOLSub, self).__init__(CLUSTER,  **kwargs_)
supermod.CLUSTER_POOL.subclass = CLUSTER_POOLSub
# end class CLUSTER_POOLSub


class CLUSTERSub(TemplatedType, supermod.CLUSTER):
    def __init__(self, ID=None, NAME=None, HOSTS=None, DATASTORES=None, VNETS=None, TEMPLATE=None, **kwargs_):
        super(CLUSTERSub, self).__init__(ID, NAME, HOSTS, DATASTORES, VNETS, TEMPLATE,  **kwargs_)
supermod.CLUSTER.subclass = CLUSTERSub
# end class CLUSTERSub


class DATASTORE_POOLSub(TemplatedType, supermod.DATASTORE_POOL):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_POOLSub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_POOL.subclass = DATASTORE_POOLSub
# end class DATASTORE_POOLSub


class DATASTORESub(TemplatedType, supermod.DATASTORE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, DS_MAD=None, TM_MAD=None, BASE_PATH=None, TYPE=None, DISK_TYPE=None, STATE=None, CLUSTERS=None, TOTAL_MB=None, FREE_MB=None, USED_MB=None, IMAGES=None, TEMPLATE=None, **kwargs_):
        super(DATASTORESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, DS_MAD, TM_MAD, BASE_PATH, TYPE, DISK_TYPE, STATE, CLUSTERS, TOTAL_MB, FREE_MB, USED_MB, IMAGES, TEMPLATE,  **kwargs_)
supermod.DATASTORE.subclass = DATASTORESub
# end class DATASTORESub


class DOCUMENT_POOLSub(TemplatedType, supermod.DOCUMENT_POOL):
    def __init__(self, DOCUMENT=None, **kwargs_):
        super(DOCUMENT_POOLSub, self).__init__(DOCUMENT,  **kwargs_)
supermod.DOCUMENT_POOL.subclass = DOCUMENT_POOLSub
# end class DOCUMENT_POOLSub


class DOCUMENTSub(TemplatedType, supermod.DOCUMENT):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, TYPE=None, PERMISSIONS=None, LOCK=None, TEMPLATE=None, **kwargs_):
        super(DOCUMENTSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, TYPE, PERMISSIONS, LOCK, TEMPLATE,  **kwargs_)
supermod.DOCUMENT.subclass = DOCUMENTSub
# end class DOCUMENTSub


class GROUP_POOLSub(TemplatedType, supermod.GROUP_POOL):
    def __init__(self, GROUP=None, QUOTAS=None, DEFAULT_GROUP_QUOTAS=None, **kwargs_):
        super(GROUP_POOLSub, self).__init__(GROUP, QUOTAS, DEFAULT_GROUP_QUOTAS,  **kwargs_)
supermod.GROUP_POOL.subclass = GROUP_POOLSub
# end class GROUP_POOLSub


class GROUPSub(TemplatedType, supermod.GROUP):
    def __init__(self, ID=None, NAME=None, TEMPLATE=None, USERS=None, ADMINS=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, DEFAULT_GROUP_QUOTAS=None, **kwargs_):
        super(GROUPSub, self).__init__(ID, NAME, TEMPLATE, USERS, ADMINS, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, DEFAULT_GROUP_QUOTAS,  **kwargs_)
supermod.GROUP.subclass = GROUPSub
# end class GROUPSub


class HOOK_MESSAGESub(TemplatedType, supermod.HOOK_MESSAGE):
    def __init__(self, HOOK_TYPE=None, CALL=None, CALL_INFO=None, **kwargs_):
        super(HOOK_MESSAGESub, self).__init__(HOOK_TYPE, CALL, CALL_INFO,  **kwargs_)
supermod.HOOK_MESSAGE.subclass = HOOK_MESSAGESub
# end class HOOK_MESSAGESub


class HOOK_POOLSub(TemplatedType, supermod.HOOK_POOL):
    def __init__(self, HOOK=None, **kwargs_):
        super(HOOK_POOLSub, self).__init__(HOOK,  **kwargs_)
supermod.HOOK_POOL.subclass = HOOK_POOLSub
# end class HOOK_POOLSub


class HOOKSub(TemplatedType, supermod.HOOK):
    def __init__(self, ID=None, NAME=None, TYPE=None, TEMPLATE=None, HOOKLOG=None, **kwargs_):
        super(HOOKSub, self).__init__(ID, NAME, TYPE, TEMPLATE, HOOKLOG,  **kwargs_)
supermod.HOOK.subclass = HOOKSub
# end class HOOKSub


class HOST_POOLSub(TemplatedType, supermod.HOST_POOL):
    def __init__(self, HOST=None, **kwargs_):
        super(HOST_POOLSub, self).__init__(HOST,  **kwargs_)
supermod.HOST_POOL.subclass = HOST_POOLSub
# end class HOST_POOLSub


class HOSTSub(TemplatedType, supermod.HOST):
    def __init__(self, ID=None, NAME=None, STATE=None, PREV_STATE=None, IM_MAD=None, VM_MAD=None, CLUSTER_ID=None, CLUSTER=None, HOST_SHARE=None, VMS=None, TEMPLATE=None, MONITORING=None, **kwargs_):
        super(HOSTSub, self).__init__(ID, NAME, STATE, PREV_STATE, IM_MAD, VM_MAD, CLUSTER_ID, CLUSTER, HOST_SHARE, VMS, TEMPLATE, MONITORING,  **kwargs_)
supermod.HOST.subclass = HOSTSub
# end class HOSTSub


class IMAGE_POOLSub(TemplatedType, supermod.IMAGE_POOL):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_POOLSub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_POOL.subclass = IMAGE_POOLSub
# end class IMAGE_POOLSub


class IMAGESub(TemplatedType, supermod.IMAGE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LOCK=None, PERMISSIONS=None, TYPE=None, DISK_TYPE=None, PERSISTENT=None, REGTIME=None, SOURCE=None, PATH=None, FORMAT=None, FS=None, SIZE=None, STATE=None, PREV_STATE=None, RUNNING_VMS=None, CLONING_OPS=None, CLONING_ID=None, TARGET_SNAPSHOT=None, DATASTORE_ID=None, DATASTORE=None, VMS=None, CLONES=None, APP_CLONES=None, TEMPLATE=None, SNAPSHOTS=None, BACKUP_INCREMENTS=None, BACKUP_DISK_IDS=None, **kwargs_):
        super(IMAGESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LOCK, PERMISSIONS, TYPE, DISK_TYPE, PERSISTENT, REGTIME, SOURCE, PATH, FORMAT, FS, SIZE, STATE, PREV_STATE, RUNNING_VMS, CLONING_OPS, CLONING_ID, TARGET_SNAPSHOT, DATASTORE_ID, DATASTORE, VMS, CLONES, APP_CLONES, TEMPLATE, SNAPSHOTS, BACKUP_INCREMENTS, BACKUP_DISK_IDS,  **kwargs_)
supermod.IMAGE.subclass = IMAGESub
# end class IMAGESub


class MARKETPLACEAPP_POOLSub(TemplatedType, supermod.MARKETPLACEAPP_POOL):
    def __init__(self, MARKETPLACEAPP=None, **kwargs_):
        super(MARKETPLACEAPP_POOLSub, self).__init__(MARKETPLACEAPP,  **kwargs_)
supermod.MARKETPLACEAPP_POOL.subclass = MARKETPLACEAPP_POOLSub
# end class MARKETPLACEAPP_POOLSub


class MARKETPLACEAPPSub(TemplatedType, supermod.MARKETPLACEAPP):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, LOCK=None, REGTIME=None, NAME=None, ZONE_ID=None, ORIGIN_ID=None, SOURCE=None, MD5=None, SIZE=None, DESCRIPTION=None, VERSION=None, FORMAT=None, APPTEMPLATE64=None, MARKETPLACE_ID=None, MARKETPLACE=None, STATE=None, TYPE=None, PERMISSIONS=None, TEMPLATE=None, **kwargs_):
        super(MARKETPLACEAPPSub, self).__init__(ID, UID, GID, UNAME, GNAME, LOCK, REGTIME, NAME, ZONE_ID, ORIGIN_ID, SOURCE, MD5, SIZE, DESCRIPTION, VERSION, FORMAT, APPTEMPLATE64, MARKETPLACE_ID, MARKETPLACE, STATE, TYPE, PERMISSIONS, TEMPLATE,  **kwargs_)
supermod.MARKETPLACEAPP.subclass = MARKETPLACEAPPSub
# end class MARKETPLACEAPPSub


class MARKETPLACE_POOLSub(TemplatedType, supermod.MARKETPLACE_POOL):
    def __init__(self, MARKETPLACE=None, **kwargs_):
        super(MARKETPLACE_POOLSub, self).__init__(MARKETPLACE,  **kwargs_)
supermod.MARKETPLACE_POOL.subclass = MARKETPLACE_POOLSub
# end class MARKETPLACE_POOLSub


class MARKETPLACESub(TemplatedType, supermod.MARKETPLACE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, STATE=None, MARKET_MAD=None, ZONE_ID=None, TOTAL_MB=None, FREE_MB=None, USED_MB=None, MARKETPLACEAPPS=None, PERMISSIONS=None, TEMPLATE=None, **kwargs_):
        super(MARKETPLACESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, STATE, MARKET_MAD, ZONE_ID, TOTAL_MB, FREE_MB, USED_MB, MARKETPLACEAPPS, PERMISSIONS, TEMPLATE,  **kwargs_)
supermod.MARKETPLACE.subclass = MARKETPLACESub
# end class MARKETPLACESub


class MONITORING_DATASub(TemplatedType, supermod.MONITORING_DATA):
    def __init__(self, MONITORING=None, **kwargs_):
        super(MONITORING_DATASub, self).__init__(MONITORING,  **kwargs_)
supermod.MONITORING_DATA.subclass = MONITORING_DATASub
# end class MONITORING_DATASub


class OPENNEBULA_CONFIGURATIONSub(TemplatedType, supermod.OPENNEBULA_CONFIGURATION):
    def __init__(self, API_LIST_ORDER=None, AUTH_MAD=None, AUTH_MAD_CONF=None, CLUSTER_ENCRYPTED_ATTR=None, CONTEXT_RESTRICTED_DIRS=None, CONTEXT_SAFE_DIRS=None, DATASTORE_CAPACITY_CHECK=None, DATASTORE_ENCRYPTED_ATTR=None, DATASTORE_LOCATION=None, DATASTORE_MAD=None, DB=None, DEFAULT_AUTH=None, DEFAULT_CDROM_DEVICE_PREFIX=None, DEFAULT_COST=None, DEFAULT_DEVICE_PREFIX=None, DEFAULT_IMAGE_PERSISTENT=None, DEFAULT_IMAGE_PERSISTENT_NEW=None, DEFAULT_IMAGE_TYPE=None, DEFAULT_UMASK=None, DEFAULT_VDC_CLUSTER_DATASTORE_ACL=None, DEFAULT_VDC_CLUSTER_HOST_ACL=None, DEFAULT_VDC_CLUSTER_NET_ACL=None, DEFAULT_VDC_DATASTORE_ACL=None, DEFAULT_VDC_HOST_ACL=None, DEFAULT_VDC_VNET_ACL=None, DOCUMENT_ENCRYPTED_ATTR=None, DS_MAD_CONF=None, DS_MONITOR_VM_DISK=None, ENABLE_OTHER_PERMISSIONS=None, FEDERATION=None, GROUP_RESTRICTED_ATTR=None, HM_MAD=None, HOOK_LOG_CONF=None, HOST_ENCRYPTED_ATTR=None, IMAGE_ENCRYPTED_ATTR=None, IMAGE_RESTRICTED_ATTR=None, IM_MAD=None, INHERIT_DATASTORE_ATTR=None, INHERIT_IMAGE_ATTR=None, INHERIT_VNET_ATTR=None, IPAM_MAD=None, KEEPALIVE_MAX_CONN=None, KEEPALIVE_TIMEOUT=None, LISTEN_ADDRESS=None, LOG=None, LOG_CALL_FORMAT=None, MAC_PREFIX=None, MANAGER_TIMER=None, MARKET_MAD=None, MARKET_MAD_CONF=None, MAX_BACKUPS=None, MAX_BACKUPS_HOST=None, MAX_CONN=None, MAX_CONN_BACKLOG=None, MESSAGE_SIZE=None, MONITORING_INTERVAL_DATASTORE=None, MONITORING_INTERVAL_HOST=None, MONITORING_INTERVAL_MARKET=None, MONITORING_INTERVAL_VM=None, NETWORK_SIZE=None, ONE_KEY=None, PCI_PASSTHROUGH_BUS=None, PORT=None, RAFT=None, RPC_LOG=None, SCRIPTS_REMOTE_DIR=None, SESSION_EXPIRATION_TIME=None, SHOWBACK_ONLY_RUNNING=None, TIMEOUT=None, TM_MAD=None, TM_MAD_CONF=None, USER_ENCRYPTED_ATTR=None, USER_RESTRICTED_ATTR=None, VLAN_IDS=None, VM_ADMIN_OPERATIONS=None, VM_ENCRYPTED_ATTR=None, VM_MAD=None, VM_MANAGE_OPERATIONS=None, VM_MONITORING_EXPIRATION_TIME=None, VM_RESTRICTED_ATTR=None, VM_SNAPSHOT_FACTOR=None, VM_SUBMIT_ON_HOLD=None, VM_USE_OPERATIONS=None, VNC_PORTS=None, VNET_ENCRYPTED_ATTR=None, VNET_RESTRICTED_ATTR=None, VN_MAD_CONF=None, VXLAN_IDS=None, **kwargs_):
        super(OPENNEBULA_CONFIGURATIONSub, self).__init__(API_LIST_ORDER, AUTH_MAD, AUTH_MAD_CONF, CLUSTER_ENCRYPTED_ATTR, CONTEXT_RESTRICTED_DIRS, CONTEXT_SAFE_DIRS, DATASTORE_CAPACITY_CHECK, DATASTORE_ENCRYPTED_ATTR, DATASTORE_LOCATION, DATASTORE_MAD, DB, DEFAULT_AUTH, DEFAULT_CDROM_DEVICE_PREFIX, DEFAULT_COST, DEFAULT_DEVICE_PREFIX, DEFAULT_IMAGE_PERSISTENT, DEFAULT_IMAGE_PERSISTENT_NEW, DEFAULT_IMAGE_TYPE, DEFAULT_UMASK, DEFAULT_VDC_CLUSTER_DATASTORE_ACL, DEFAULT_VDC_CLUSTER_HOST_ACL, DEFAULT_VDC_CLUSTER_NET_ACL, DEFAULT_VDC_DATASTORE_ACL, DEFAULT_VDC_HOST_ACL, DEFAULT_VDC_VNET_ACL, DOCUMENT_ENCRYPTED_ATTR, DS_MAD_CONF, DS_MONITOR_VM_DISK, ENABLE_OTHER_PERMISSIONS, FEDERATION, GROUP_RESTRICTED_ATTR, HM_MAD, HOOK_LOG_CONF, HOST_ENCRYPTED_ATTR, IMAGE_ENCRYPTED_ATTR, IMAGE_RESTRICTED_ATTR, IM_MAD, INHERIT_DATASTORE_ATTR, INHERIT_IMAGE_ATTR, INHERIT_VNET_ATTR, IPAM_MAD, KEEPALIVE_MAX_CONN, KEEPALIVE_TIMEOUT, LISTEN_ADDRESS, LOG, LOG_CALL_FORMAT, MAC_PREFIX, MANAGER_TIMER, MARKET_MAD, MARKET_MAD_CONF, MAX_BACKUPS, MAX_BACKUPS_HOST, MAX_CONN, MAX_CONN_BACKLOG, MESSAGE_SIZE, MONITORING_INTERVAL_DATASTORE, MONITORING_INTERVAL_HOST, MONITORING_INTERVAL_MARKET, MONITORING_INTERVAL_VM, NETWORK_SIZE, ONE_KEY, PCI_PASSTHROUGH_BUS, PORT, RAFT, RPC_LOG, SCRIPTS_REMOTE_DIR, SESSION_EXPIRATION_TIME, SHOWBACK_ONLY_RUNNING, TIMEOUT, TM_MAD, TM_MAD_CONF, USER_ENCRYPTED_ATTR, USER_RESTRICTED_ATTR, VLAN_IDS, VM_ADMIN_OPERATIONS, VM_ENCRYPTED_ATTR, VM_MAD, VM_MANAGE_OPERATIONS, VM_MONITORING_EXPIRATION_TIME, VM_RESTRICTED_ATTR, VM_SNAPSHOT_FACTOR, VM_SUBMIT_ON_HOLD, VM_USE_OPERATIONS, VNC_PORTS, VNET_ENCRYPTED_ATTR, VNET_RESTRICTED_ATTR, VN_MAD_CONF, VXLAN_IDS,  **kwargs_)
supermod.OPENNEBULA_CONFIGURATION.subclass = OPENNEBULA_CONFIGURATIONSub
# end class OPENNEBULA_CONFIGURATIONSub


class RAFTSub(TemplatedType, supermod.RAFT):
    def __init__(self, SERVER_ID=None, STATE=None, TERM=None, VOTEDFOR=None, COMMIT=None, LOG_INDEX=None, LOG_TERM=None, FEDLOG_INDEX=None, **kwargs_):
        super(RAFTSub, self).__init__(SERVER_ID, STATE, TERM, VOTEDFOR, COMMIT, LOG_INDEX, LOG_TERM, FEDLOG_INDEX,  **kwargs_)
supermod.RAFT.subclass = RAFTSub
# end class RAFTSub


class SECURITY_GROUP_POOLSub(TemplatedType, supermod.SECURITY_GROUP_POOL):
    def __init__(self, SECURITY_GROUP=None, **kwargs_):
        super(SECURITY_GROUP_POOLSub, self).__init__(SECURITY_GROUP,  **kwargs_)
supermod.SECURITY_GROUP_POOL.subclass = SECURITY_GROUP_POOLSub
# end class SECURITY_GROUP_POOLSub


class SECURITY_GROUPSub(TemplatedType, supermod.SECURITY_GROUP):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, UPDATED_VMS=None, OUTDATED_VMS=None, UPDATING_VMS=None, ERROR_VMS=None, TEMPLATE=None, **kwargs_):
        super(SECURITY_GROUPSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, UPDATED_VMS, OUTDATED_VMS, UPDATING_VMS, ERROR_VMS, TEMPLATE,  **kwargs_)
supermod.SECURITY_GROUP.subclass = SECURITY_GROUPSub
# end class SECURITY_GROUPSub


class SHOWBACK_RECORDSSub(TemplatedType, supermod.SHOWBACK_RECORDS):
    def __init__(self, SHOWBACK=None, **kwargs_):
        super(SHOWBACK_RECORDSSub, self).__init__(SHOWBACK,  **kwargs_)
supermod.SHOWBACK_RECORDS.subclass = SHOWBACK_RECORDSSub
# end class SHOWBACK_RECORDSSub


class USER_POOLSub(TemplatedType, supermod.USER_POOL):
    def __init__(self, USER=None, QUOTAS=None, DEFAULT_USER_QUOTAS=None, **kwargs_):
        super(USER_POOLSub, self).__init__(USER, QUOTAS, DEFAULT_USER_QUOTAS,  **kwargs_)
supermod.USER_POOL.subclass = USER_POOLSub
# end class USER_POOLSub


class USERSub(TemplatedType, supermod.USER):
    def __init__(self, ID=None, GID=None, GROUPS=None, GNAME=None, NAME=None, PASSWORD=None, AUTH_DRIVER=None, ENABLED=None, LOGIN_TOKEN=None, TEMPLATE=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, DEFAULT_USER_QUOTAS=None, **kwargs_):
        super(USERSub, self).__init__(ID, GID, GROUPS, GNAME, NAME, PASSWORD, AUTH_DRIVER, ENABLED, LOGIN_TOKEN, TEMPLATE, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA, DEFAULT_USER_QUOTAS,  **kwargs_)
supermod.USER.subclass = USERSub
# end class USERSub


class VDC_POOLSub(TemplatedType, supermod.VDC_POOL):
    def __init__(self, VDC=None, **kwargs_):
        super(VDC_POOLSub, self).__init__(VDC,  **kwargs_)
supermod.VDC_POOL.subclass = VDC_POOLSub
# end class VDC_POOLSub


class VDCSub(TemplatedType, supermod.VDC):
    def __init__(self, ID=None, NAME=None, GROUPS=None, CLUSTERS=None, HOSTS=None, DATASTORES=None, VNETS=None, TEMPLATE=None, **kwargs_):
        super(VDCSub, self).__init__(ID, NAME, GROUPS, CLUSTERS, HOSTS, DATASTORES, VNETS, TEMPLATE,  **kwargs_)
supermod.VDC.subclass = VDCSub
# end class VDCSub


class VM_GROUP_POOLSub(TemplatedType, supermod.VM_GROUP_POOL):
    def __init__(self, VM_GROUP=None, **kwargs_):
        super(VM_GROUP_POOLSub, self).__init__(VM_GROUP,  **kwargs_)
supermod.VM_GROUP_POOL.subclass = VM_GROUP_POOLSub
# end class VM_GROUP_POOLSub


class VM_GROUPSub(TemplatedType, supermod.VM_GROUP):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LOCK=None, ROLES=None, TEMPLATE=None, **kwargs_):
        super(VM_GROUPSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LOCK, ROLES, TEMPLATE,  **kwargs_)
supermod.VM_GROUP.subclass = VM_GROUPSub
# end class VM_GROUPSub


class VM_POOLSub(TemplatedType, supermod.VM_POOL):
    def __init__(self, VM=None, **kwargs_):
        super(VM_POOLSub, self).__init__(VM,  **kwargs_)
supermod.VM_POOL.subclass = VM_POOLSub
# end class VM_POOLSub


class VMTEMPLATE_POOLSub(TemplatedType, supermod.VMTEMPLATE_POOL):
    def __init__(self, VMTEMPLATE=None, **kwargs_):
        super(VMTEMPLATE_POOLSub, self).__init__(VMTEMPLATE,  **kwargs_)
supermod.VMTEMPLATE_POOL.subclass = VMTEMPLATE_POOLSub
# end class VMTEMPLATE_POOLSub


class VMTEMPLATESub(TemplatedType, supermod.VMTEMPLATE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LOCK=None, PERMISSIONS=None, REGTIME=None, TEMPLATE=None, **kwargs_):
        super(VMTEMPLATESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LOCK, PERMISSIONS, REGTIME, TEMPLATE,  **kwargs_)
supermod.VMTEMPLATE.subclass = VMTEMPLATESub
# end class VMTEMPLATESub


class VMSub(TemplatedType, supermod.VM):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LAST_POLL=None, STATE=None, LCM_STATE=None, PREV_STATE=None, PREV_LCM_STATE=None, RESCHED=None, STIME=None, ETIME=None, DEPLOY_ID=None, LOCK=None, MONITORING=None, SCHED_ACTIONS=None, TEMPLATE=None, USER_TEMPLATE=None, HISTORY_RECORDS=None, SNAPSHOTS=None, BACKUPS=None, **kwargs_):
        super(VMSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LAST_POLL, STATE, LCM_STATE, PREV_STATE, PREV_LCM_STATE, RESCHED, STIME, ETIME, DEPLOY_ID, LOCK, MONITORING, SCHED_ACTIONS, TEMPLATE, USER_TEMPLATE, HISTORY_RECORDS, SNAPSHOTS, BACKUPS,  **kwargs_)
supermod.VM.subclass = VMSub
# end class VMSub


class VNET_POOLSub(TemplatedType, supermod.VNET_POOL):
    def __init__(self, VNET=None, **kwargs_):
        super(VNET_POOLSub, self).__init__(VNET,  **kwargs_)
supermod.VNET_POOL.subclass = VNET_POOLSub
# end class VNET_POOLSub


class VNETSub(TemplatedType, supermod.VNET):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LOCK=None, PERMISSIONS=None, CLUSTERS=None, BRIDGE=None, BRIDGE_TYPE=None, STATE=None, PREV_STATE=None, PARENT_NETWORK_ID=None, VN_MAD=None, PHYDEV=None, VLAN_ID=None, OUTER_VLAN_ID=None, VLAN_ID_AUTOMATIC=None, OUTER_VLAN_ID_AUTOMATIC=None, USED_LEASES=None, VROUTERS=None, UPDATED_VMS=None, OUTDATED_VMS=None, UPDATING_VMS=None, ERROR_VMS=None, TEMPLATE=None, AR_POOL=None, **kwargs_):
        super(VNETSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LOCK, PERMISSIONS, CLUSTERS, BRIDGE, BRIDGE_TYPE, STATE, PREV_STATE, PARENT_NETWORK_ID, VN_MAD, PHYDEV, VLAN_ID, OUTER_VLAN_ID, VLAN_ID_AUTOMATIC, OUTER_VLAN_ID_AUTOMATIC, USED_LEASES, VROUTERS, UPDATED_VMS, OUTDATED_VMS, UPDATING_VMS, ERROR_VMS, TEMPLATE, AR_POOL,  **kwargs_)
supermod.VNET.subclass = VNETSub
# end class VNETSub


class VNTEMPLATE_POOLSub(TemplatedType, supermod.VNTEMPLATE_POOL):
    def __init__(self, VNTEMPLATE=None, **kwargs_):
        super(VNTEMPLATE_POOLSub, self).__init__(VNTEMPLATE,  **kwargs_)
supermod.VNTEMPLATE_POOL.subclass = VNTEMPLATE_POOLSub
# end class VNTEMPLATE_POOLSub


class VNTEMPLATESub(TemplatedType, supermod.VNTEMPLATE):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LOCK=None, PERMISSIONS=None, REGTIME=None, TEMPLATE=None, **kwargs_):
        super(VNTEMPLATESub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LOCK, PERMISSIONS, REGTIME, TEMPLATE,  **kwargs_)
supermod.VNTEMPLATE.subclass = VNTEMPLATESub
# end class VNTEMPLATESub


class VROUTER_POOLSub(TemplatedType, supermod.VROUTER_POOL):
    def __init__(self, VROUTER=None, **kwargs_):
        super(VROUTER_POOLSub, self).__init__(VROUTER,  **kwargs_)
supermod.VROUTER_POOL.subclass = VROUTER_POOLSub
# end class VROUTER_POOLSub


class VROUTERSub(TemplatedType, supermod.VROUTER):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LOCK=None, VMS=None, TEMPLATE=None, **kwargs_):
        super(VROUTERSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LOCK, VMS, TEMPLATE,  **kwargs_)
supermod.VROUTER.subclass = VROUTERSub
# end class VROUTERSub


class ZONE_POOLSub(TemplatedType, supermod.ZONE_POOL):
    def __init__(self, ZONE=None, **kwargs_):
        super(ZONE_POOLSub, self).__init__(ZONE,  **kwargs_)
supermod.ZONE_POOL.subclass = ZONE_POOLSub
# end class ZONE_POOLSub


class ZONESub(TemplatedType, supermod.ZONE):
    def __init__(self, ID=None, NAME=None, STATE=None, TEMPLATE=None, SERVER_POOL=None, **kwargs_):
        super(ZONESub, self).__init__(ID, NAME, STATE, TEMPLATE, SERVER_POOL,  **kwargs_)
supermod.ZONE.subclass = ZONESub
# end class ZONESub


class VMTypeSub(TemplatedType, supermod.VMType):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, LAST_POLL=None, STATE=None, LCM_STATE=None, PREV_STATE=None, PREV_LCM_STATE=None, RESCHED=None, STIME=None, ETIME=None, DEPLOY_ID=None, MONITORING=None, SCHED_ACTIONS=None, TEMPLATE=None, USER_TEMPLATE=None, HISTORY_RECORDS=None, SNAPSHOTS=None, BACKUPS=None, **kwargs_):
        super(VMTypeSub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, LAST_POLL, STATE, LCM_STATE, PREV_STATE, PREV_LCM_STATE, RESCHED, STIME, ETIME, DEPLOY_ID, MONITORING, SCHED_ACTIONS, TEMPLATE, USER_TEMPLATE, HISTORY_RECORDS, SNAPSHOTS, BACKUPS,  **kwargs_)
supermod.VMType.subclass = VMTypeSub
# end class VMTypeSub


class PERMISSIONSTypeSub(TemplatedType, supermod.PERMISSIONSType):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSTypeSub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType.subclass = PERMISSIONSTypeSub
# end class PERMISSIONSTypeSub


class SNAPSHOTSTypeSub(TemplatedType, supermod.SNAPSHOTSType):
    def __init__(self, ALLOW_ORPHANS=None, CURRENT_BASE=None, DISK_ID=None, NEXT_SNAPSHOT=None, SNAPSHOT=None, **kwargs_):
        super(SNAPSHOTSTypeSub, self).__init__(ALLOW_ORPHANS, CURRENT_BASE, DISK_ID, NEXT_SNAPSHOT, SNAPSHOT,  **kwargs_)
supermod.SNAPSHOTSType.subclass = SNAPSHOTSTypeSub
# end class SNAPSHOTSTypeSub


class SNAPSHOTTypeSub(TemplatedType, supermod.SNAPSHOTType):
    def __init__(self, ACTIVE=None, CHILDREN=None, DATE=None, ID=None, NAME=None, PARENT=None, SIZE=None, **kwargs_):
        super(SNAPSHOTTypeSub, self).__init__(ACTIVE, CHILDREN, DATE, ID, NAME, PARENT, SIZE,  **kwargs_)
supermod.SNAPSHOTType.subclass = SNAPSHOTTypeSub
# end class SNAPSHOTTypeSub


class BACKUPSTypeSub(TemplatedType, supermod.BACKUPSType):
    def __init__(self, BACKUP_CONFIG=None, BACKUP_IDS=None, **kwargs_):
        super(BACKUPSTypeSub, self).__init__(BACKUP_CONFIG, BACKUP_IDS,  **kwargs_)
supermod.BACKUPSType.subclass = BACKUPSTypeSub
# end class BACKUPSTypeSub


class BACKUP_CONFIGTypeSub(TemplatedType, supermod.BACKUP_CONFIGType):
    def __init__(self, BACKUP_VOLATILE=None, FS_FREEZE=None, INCREMENTAL_BACKUP_ID=None, INCREMENT_MODE=None, KEEP_LAST=None, LAST_BACKUP_ID=None, LAST_BACKUP_SIZE=None, LAST_DATASTORE_ID=None, LAST_INCREMENT_ID=None, MODE=None, **kwargs_):
        super(BACKUP_CONFIGTypeSub, self).__init__(BACKUP_VOLATILE, FS_FREEZE, INCREMENTAL_BACKUP_ID, INCREMENT_MODE, KEEP_LAST, LAST_BACKUP_ID, LAST_BACKUP_SIZE, LAST_DATASTORE_ID, LAST_INCREMENT_ID, MODE,  **kwargs_)
supermod.BACKUP_CONFIGType.subclass = BACKUP_CONFIGTypeSub
# end class BACKUP_CONFIGTypeSub


class BACKUP_IDSTypeSub(TemplatedType, supermod.BACKUP_IDSType):
    def __init__(self, ID=None, **kwargs_):
        super(BACKUP_IDSTypeSub, self).__init__(ID,  **kwargs_)
supermod.BACKUP_IDSType.subclass = BACKUP_IDSTypeSub
# end class BACKUP_IDSTypeSub


class ACLTypeSub(TemplatedType, supermod.ACLType):
    def __init__(self, ID=None, USER=None, RESOURCE=None, RIGHTS=None, ZONE=None, STRING=None, **kwargs_):
        super(ACLTypeSub, self).__init__(ID, USER, RESOURCE, RIGHTS, ZONE, STRING,  **kwargs_)
supermod.ACLType.subclass = ACLTypeSub
# end class ACLTypeSub


class PARAMETERSTypeSub(TemplatedType, supermod.PARAMETERSType):
    def __init__(self, PARAMETER=None, **kwargs_):
        super(PARAMETERSTypeSub, self).__init__(PARAMETER,  **kwargs_)
supermod.PARAMETERSType.subclass = PARAMETERSTypeSub
# end class PARAMETERSTypeSub


class PARAMETERTypeSub(TemplatedType, supermod.PARAMETERType):
    def __init__(self, POSITION=None, TYPE=None, VALUE=None, **kwargs_):
        super(PARAMETERTypeSub, self).__init__(POSITION, TYPE, VALUE,  **kwargs_)
supermod.PARAMETERType.subclass = PARAMETERTypeSub
# end class PARAMETERTypeSub


class EXTRATypeSub(TemplatedType, supermod.EXTRAType):
    def __init__(self, anytypeobjs_=None, **kwargs_):
        super(EXTRATypeSub, self).__init__(anytypeobjs_,  **kwargs_)
supermod.EXTRAType.subclass = EXTRATypeSub
# end class EXTRATypeSub


class TEMPLATETypeSub(TemplatedType, supermod.TEMPLATEType):
    def __init__(self, BACKUP_VMS=None, BACKUP_VOLATILE=None, DATASTORE_ID=None, ERROR=None, EXECUTION=None, FS_FREEZE=None, KEEP_LAST=None, MODE=None, RESET=None, SCHED_ACTION=None, **kwargs_):
        super(TEMPLATETypeSub, self).__init__(BACKUP_VMS, BACKUP_VOLATILE, DATASTORE_ID, ERROR, EXECUTION, FS_FREEZE, KEEP_LAST, MODE, RESET, SCHED_ACTION,  **kwargs_)
supermod.TEMPLATEType.subclass = TEMPLATETypeSub
# end class TEMPLATETypeSub


class HOSTSTypeSub(TemplatedType, supermod.HOSTSType):
    def __init__(self, ID=None, **kwargs_):
        super(HOSTSTypeSub, self).__init__(ID,  **kwargs_)
supermod.HOSTSType.subclass = HOSTSTypeSub
# end class HOSTSTypeSub


class DATASTORESTypeSub(TemplatedType, supermod.DATASTORESType):
    def __init__(self, ID=None, **kwargs_):
        super(DATASTORESTypeSub, self).__init__(ID,  **kwargs_)
supermod.DATASTORESType.subclass = DATASTORESTypeSub
# end class DATASTORESTypeSub


class VNETSTypeSub(TemplatedType, supermod.VNETSType):
    def __init__(self, ID=None, **kwargs_):
        super(VNETSTypeSub, self).__init__(ID,  **kwargs_)
supermod.VNETSType.subclass = VNETSTypeSub
# end class VNETSTypeSub


class PERMISSIONSType1Sub(TemplatedType, supermod.PERMISSIONSType1):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType1Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType1.subclass = PERMISSIONSType1Sub
# end class PERMISSIONSType1Sub


class CLUSTERSTypeSub(TemplatedType, supermod.CLUSTERSType):
    def __init__(self, ID=None, **kwargs_):
        super(CLUSTERSTypeSub, self).__init__(ID,  **kwargs_)
supermod.CLUSTERSType.subclass = CLUSTERSTypeSub
# end class CLUSTERSTypeSub


class IMAGESTypeSub(TemplatedType, supermod.IMAGESType):
    def __init__(self, ID=None, **kwargs_):
        super(IMAGESTypeSub, self).__init__(ID,  **kwargs_)
supermod.IMAGESType.subclass = IMAGESTypeSub
# end class IMAGESTypeSub


class TEMPLATEType2Sub(TemplatedType, supermod.TEMPLATEType2):
    def __init__(self, VCENTER_DC_NAME=None, VCENTER_DC_REF=None, VCENTER_DS_NAME=None, VCENTER_DS_REF=None, VCENTER_HOST=None, VCENTER_INSTANCE_ID=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType2Sub, self).__init__(VCENTER_DC_NAME, VCENTER_DC_REF, VCENTER_DS_NAME, VCENTER_DS_REF, VCENTER_HOST, VCENTER_INSTANCE_ID, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType2.subclass = TEMPLATEType2Sub
# end class TEMPLATEType2Sub


class PERMISSIONSType3Sub(TemplatedType, supermod.PERMISSIONSType3):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType3Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType3.subclass = PERMISSIONSType3Sub
# end class PERMISSIONSType3Sub


class LOCKTypeSub(TemplatedType, supermod.LOCKType):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKTypeSub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType.subclass = LOCKTypeSub
# end class LOCKTypeSub


class GROUPTypeSub(TemplatedType, supermod.GROUPType):
    def __init__(self, ID=None, NAME=None, TEMPLATE=None, USERS=None, ADMINS=None, **kwargs_):
        super(GROUPTypeSub, self).__init__(ID, NAME, TEMPLATE, USERS, ADMINS,  **kwargs_)
supermod.GROUPType.subclass = GROUPTypeSub
# end class GROUPTypeSub


class USERSTypeSub(TemplatedType, supermod.USERSType):
    def __init__(self, ID=None, **kwargs_):
        super(USERSTypeSub, self).__init__(ID,  **kwargs_)
supermod.USERSType.subclass = USERSTypeSub
# end class USERSTypeSub


class ADMINSTypeSub(TemplatedType, supermod.ADMINSType):
    def __init__(self, ID=None, **kwargs_):
        super(ADMINSTypeSub, self).__init__(ID,  **kwargs_)
supermod.ADMINSType.subclass = ADMINSTypeSub
# end class ADMINSTypeSub


class QUOTASTypeSub(TemplatedType, supermod.QUOTASType):
    def __init__(self, ID=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(QUOTASTypeSub, self).__init__(ID, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.QUOTASType.subclass = QUOTASTypeSub
# end class QUOTASTypeSub


class DATASTORE_QUOTATypeSub(TemplatedType, supermod.DATASTORE_QUOTAType):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTATypeSub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType.subclass = DATASTORE_QUOTATypeSub
# end class DATASTORE_QUOTATypeSub


class DATASTORETypeSub(TemplatedType, supermod.DATASTOREType):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTORETypeSub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType.subclass = DATASTORETypeSub
# end class DATASTORETypeSub


class NETWORK_QUOTATypeSub(TemplatedType, supermod.NETWORK_QUOTAType):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTATypeSub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType.subclass = NETWORK_QUOTATypeSub
# end class NETWORK_QUOTATypeSub


class NETWORKTypeSub(TemplatedType, supermod.NETWORKType):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKTypeSub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType.subclass = NETWORKTypeSub
# end class NETWORKTypeSub


class VM_QUOTATypeSub(TemplatedType, supermod.VM_QUOTAType):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTATypeSub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType.subclass = VM_QUOTATypeSub
# end class VM_QUOTATypeSub


class VMType4Sub(TemplatedType, supermod.VMType4):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType4Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType4.subclass = VMType4Sub
# end class VMType4Sub


class IMAGE_QUOTATypeSub(TemplatedType, supermod.IMAGE_QUOTAType):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTATypeSub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType.subclass = IMAGE_QUOTATypeSub
# end class IMAGE_QUOTATypeSub


class IMAGETypeSub(TemplatedType, supermod.IMAGEType):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGETypeSub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType.subclass = IMAGETypeSub
# end class IMAGETypeSub


class DEFAULT_GROUP_QUOTASTypeSub(TemplatedType, supermod.DEFAULT_GROUP_QUOTASType):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(DEFAULT_GROUP_QUOTASTypeSub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.DEFAULT_GROUP_QUOTASType.subclass = DEFAULT_GROUP_QUOTASTypeSub
# end class DEFAULT_GROUP_QUOTASTypeSub


class DATASTORE_QUOTAType5Sub(TemplatedType, supermod.DATASTORE_QUOTAType5):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType5Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType5.subclass = DATASTORE_QUOTAType5Sub
# end class DATASTORE_QUOTAType5Sub


class DATASTOREType6Sub(TemplatedType, supermod.DATASTOREType6):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType6Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType6.subclass = DATASTOREType6Sub
# end class DATASTOREType6Sub


class NETWORK_QUOTAType7Sub(TemplatedType, supermod.NETWORK_QUOTAType7):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType7Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType7.subclass = NETWORK_QUOTAType7Sub
# end class NETWORK_QUOTAType7Sub


class NETWORKType8Sub(TemplatedType, supermod.NETWORKType8):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType8Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType8.subclass = NETWORKType8Sub
# end class NETWORKType8Sub


class VM_QUOTAType9Sub(TemplatedType, supermod.VM_QUOTAType9):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType9Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType9.subclass = VM_QUOTAType9Sub
# end class VM_QUOTAType9Sub


class VMType10Sub(TemplatedType, supermod.VMType10):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType10Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType10.subclass = VMType10Sub
# end class VMType10Sub


class IMAGE_QUOTAType11Sub(TemplatedType, supermod.IMAGE_QUOTAType11):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType11Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType11.subclass = IMAGE_QUOTAType11Sub
# end class IMAGE_QUOTAType11Sub


class IMAGEType12Sub(TemplatedType, supermod.IMAGEType12):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType12Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType12.subclass = IMAGEType12Sub
# end class IMAGEType12Sub


class USERSType13Sub(TemplatedType, supermod.USERSType13):
    def __init__(self, ID=None, **kwargs_):
        super(USERSType13Sub, self).__init__(ID,  **kwargs_)
supermod.USERSType13.subclass = USERSType13Sub
# end class USERSType13Sub


class ADMINSType14Sub(TemplatedType, supermod.ADMINSType14):
    def __init__(self, ID=None, **kwargs_):
        super(ADMINSType14Sub, self).__init__(ID,  **kwargs_)
supermod.ADMINSType14.subclass = ADMINSType14Sub
# end class ADMINSType14Sub


class DATASTORE_QUOTAType15Sub(TemplatedType, supermod.DATASTORE_QUOTAType15):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType15Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType15.subclass = DATASTORE_QUOTAType15Sub
# end class DATASTORE_QUOTAType15Sub


class DATASTOREType16Sub(TemplatedType, supermod.DATASTOREType16):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType16Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType16.subclass = DATASTOREType16Sub
# end class DATASTOREType16Sub


class NETWORK_QUOTAType17Sub(TemplatedType, supermod.NETWORK_QUOTAType17):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType17Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType17.subclass = NETWORK_QUOTAType17Sub
# end class NETWORK_QUOTAType17Sub


class NETWORKType18Sub(TemplatedType, supermod.NETWORKType18):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType18Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType18.subclass = NETWORKType18Sub
# end class NETWORKType18Sub


class VM_QUOTAType19Sub(TemplatedType, supermod.VM_QUOTAType19):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType19Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType19.subclass = VM_QUOTAType19Sub
# end class VM_QUOTAType19Sub


class VMType20Sub(TemplatedType, supermod.VMType20):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType20Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType20.subclass = VMType20Sub
# end class VMType20Sub


class IMAGE_QUOTAType21Sub(TemplatedType, supermod.IMAGE_QUOTAType21):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType21Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType21.subclass = IMAGE_QUOTAType21Sub
# end class IMAGE_QUOTAType21Sub


class IMAGEType22Sub(TemplatedType, supermod.IMAGEType22):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType22Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType22.subclass = IMAGEType22Sub
# end class IMAGEType22Sub


class DEFAULT_GROUP_QUOTASType23Sub(TemplatedType, supermod.DEFAULT_GROUP_QUOTASType23):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(DEFAULT_GROUP_QUOTASType23Sub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.DEFAULT_GROUP_QUOTASType23.subclass = DEFAULT_GROUP_QUOTASType23Sub
# end class DEFAULT_GROUP_QUOTASType23Sub


class DATASTORE_QUOTAType24Sub(TemplatedType, supermod.DATASTORE_QUOTAType24):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType24Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType24.subclass = DATASTORE_QUOTAType24Sub
# end class DATASTORE_QUOTAType24Sub


class DATASTOREType25Sub(TemplatedType, supermod.DATASTOREType25):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType25Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType25.subclass = DATASTOREType25Sub
# end class DATASTOREType25Sub


class NETWORK_QUOTAType26Sub(TemplatedType, supermod.NETWORK_QUOTAType26):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType26Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType26.subclass = NETWORK_QUOTAType26Sub
# end class NETWORK_QUOTAType26Sub


class NETWORKType27Sub(TemplatedType, supermod.NETWORKType27):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType27Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType27.subclass = NETWORKType27Sub
# end class NETWORKType27Sub


class VM_QUOTAType28Sub(TemplatedType, supermod.VM_QUOTAType28):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType28Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType28.subclass = VM_QUOTAType28Sub
# end class VM_QUOTAType28Sub


class VMType29Sub(TemplatedType, supermod.VMType29):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType29Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType29.subclass = VMType29Sub
# end class VMType29Sub


class IMAGE_QUOTAType30Sub(TemplatedType, supermod.IMAGE_QUOTAType30):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType30Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType30.subclass = IMAGE_QUOTAType30Sub
# end class IMAGE_QUOTAType30Sub


class IMAGEType31Sub(TemplatedType, supermod.IMAGEType31):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType31Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType31.subclass = IMAGEType31Sub
# end class IMAGEType31Sub


class TEMPLATEType32Sub(TemplatedType, supermod.TEMPLATEType32):
    def __init__(self, ARGUMENTS=None, ARGUMENTS_STDIN=None, CALL=None, COMMAND=None, REMOTE=None, RESOURCE=None, STATE=None, LCM_STATE=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType32Sub, self).__init__(ARGUMENTS, ARGUMENTS_STDIN, CALL, COMMAND, REMOTE, RESOURCE, STATE, LCM_STATE, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType32.subclass = TEMPLATEType32Sub
# end class TEMPLATEType32Sub


class HOOKLOGTypeSub(TemplatedType, supermod.HOOKLOGType):
    def __init__(self, HOOK_EXECUTION_RECORD=None, **kwargs_):
        super(HOOKLOGTypeSub, self).__init__(HOOK_EXECUTION_RECORD,  **kwargs_)
supermod.HOOKLOGType.subclass = HOOKLOGTypeSub
# end class HOOKLOGTypeSub


class HOOK_EXECUTION_RECORDTypeSub(TemplatedType, supermod.HOOK_EXECUTION_RECORDType):
    def __init__(self, HOOK_ID=None, EXECUTION_ID=None, TIMESTAMP=None, ARGUMENTS=None, EXECUTION_RESULT=None, REMOTE_HOST=None, RETRY=None, anytypeobjs_=None, **kwargs_):
        super(HOOK_EXECUTION_RECORDTypeSub, self).__init__(HOOK_ID, EXECUTION_ID, TIMESTAMP, ARGUMENTS, EXECUTION_RESULT, REMOTE_HOST, RETRY, anytypeobjs_,  **kwargs_)
supermod.HOOK_EXECUTION_RECORDType.subclass = HOOK_EXECUTION_RECORDTypeSub
# end class HOOK_EXECUTION_RECORDTypeSub


class EXECUTION_RESULTTypeSub(TemplatedType, supermod.EXECUTION_RESULTType):
    def __init__(self, COMMAND=None, STDOUT=None, STDERR=None, CODE=None, **kwargs_):
        super(EXECUTION_RESULTTypeSub, self).__init__(COMMAND, STDOUT, STDERR, CODE,  **kwargs_)
supermod.EXECUTION_RESULTType.subclass = EXECUTION_RESULTTypeSub
# end class EXECUTION_RESULTTypeSub


class HOST_SHARETypeSub(TemplatedType, supermod.HOST_SHAREType):
    def __init__(self, MEM_USAGE=None, CPU_USAGE=None, TOTAL_MEM=None, TOTAL_CPU=None, MAX_MEM=None, MAX_CPU=None, RUNNING_VMS=None, VMS_THREAD=None, DATASTORES=None, PCI_DEVICES=None, NUMA_NODES=None, **kwargs_):
        super(HOST_SHARETypeSub, self).__init__(MEM_USAGE, CPU_USAGE, TOTAL_MEM, TOTAL_CPU, MAX_MEM, MAX_CPU, RUNNING_VMS, VMS_THREAD, DATASTORES, PCI_DEVICES, NUMA_NODES,  **kwargs_)
supermod.HOST_SHAREType.subclass = HOST_SHARETypeSub
# end class HOST_SHARETypeSub


class DATASTORESType33Sub(TemplatedType, supermod.DATASTORESType33):
    def __init__(self, DISK_USAGE=None, DS=None, FREE_DISK=None, MAX_DISK=None, USED_DISK=None, **kwargs_):
        super(DATASTORESType33Sub, self).__init__(DISK_USAGE, DS, FREE_DISK, MAX_DISK, USED_DISK,  **kwargs_)
supermod.DATASTORESType33.subclass = DATASTORESType33Sub
# end class DATASTORESType33Sub


class DSTypeSub(TemplatedType, supermod.DSType):
    def __init__(self, FREE_MB=None, ID=None, TOTAL_MB=None, USED_MB=None, REPLICA_CACHE=None, REPLICA_CACHE_SIZE=None, REPLICA_IMAGES=None, **kwargs_):
        super(DSTypeSub, self).__init__(FREE_MB, ID, TOTAL_MB, USED_MB, REPLICA_CACHE, REPLICA_CACHE_SIZE, REPLICA_IMAGES,  **kwargs_)
supermod.DSType.subclass = DSTypeSub
# end class DSTypeSub


class PCI_DEVICESTypeSub(TemplatedType, supermod.PCI_DEVICESType):
    def __init__(self, PCI=None, **kwargs_):
        super(PCI_DEVICESTypeSub, self).__init__(PCI,  **kwargs_)
supermod.PCI_DEVICESType.subclass = PCI_DEVICESTypeSub
# end class PCI_DEVICESTypeSub


class PCITypeSub(TemplatedType, supermod.PCIType):
    def __init__(self, ADDRESS=None, BUS=None, CLASS=None, CLASS_NAME=None, DEVICE=None, DEVICE_NAME=None, DOMAIN=None, FUNCTION=None, NUMA_NODE=None, PROFILES=None, SHORT_ADDRESS=None, SLOT=None, TYPE=None, UUID=None, VENDOR=None, VENDOR_NAME=None, VMID=None, **kwargs_):
        super(PCITypeSub, self).__init__(ADDRESS, BUS, CLASS, CLASS_NAME, DEVICE, DEVICE_NAME, DOMAIN, FUNCTION, NUMA_NODE, PROFILES, SHORT_ADDRESS, SLOT, TYPE, UUID, VENDOR, VENDOR_NAME, VMID,  **kwargs_)
supermod.PCIType.subclass = PCITypeSub
# end class PCITypeSub


class NUMA_NODESTypeSub(TemplatedType, supermod.NUMA_NODESType):
    def __init__(self, NODE=None, **kwargs_):
        super(NUMA_NODESTypeSub, self).__init__(NODE,  **kwargs_)
supermod.NUMA_NODESType.subclass = NUMA_NODESTypeSub
# end class NUMA_NODESTypeSub


class NODETypeSub(TemplatedType, supermod.NODEType):
    def __init__(self, CORE=None, HUGEPAGE=None, MEMORY=None, NODE_ID=None, **kwargs_):
        super(NODETypeSub, self).__init__(CORE, HUGEPAGE, MEMORY, NODE_ID,  **kwargs_)
supermod.NODEType.subclass = NODETypeSub
# end class NODETypeSub


class CORETypeSub(TemplatedType, supermod.COREType):
    def __init__(self, CPUS=None, DEDICATED=None, FREE=None, ID=None, **kwargs_):
        super(CORETypeSub, self).__init__(CPUS, DEDICATED, FREE, ID,  **kwargs_)
supermod.COREType.subclass = CORETypeSub
# end class CORETypeSub


class HUGEPAGETypeSub(TemplatedType, supermod.HUGEPAGEType):
    def __init__(self, PAGES=None, SIZE=None, USAGE=None, **kwargs_):
        super(HUGEPAGETypeSub, self).__init__(PAGES, SIZE, USAGE,  **kwargs_)
supermod.HUGEPAGEType.subclass = HUGEPAGETypeSub
# end class HUGEPAGETypeSub


class MEMORYTypeSub(TemplatedType, supermod.MEMORYType):
    def __init__(self, DISTANCE=None, TOTAL=None, USAGE=None, **kwargs_):
        super(MEMORYTypeSub, self).__init__(DISTANCE, TOTAL, USAGE,  **kwargs_)
supermod.MEMORYType.subclass = MEMORYTypeSub
# end class MEMORYTypeSub


class VMSTypeSub(TemplatedType, supermod.VMSType):
    def __init__(self, ID=None, **kwargs_):
        super(VMSTypeSub, self).__init__(ID,  **kwargs_)
supermod.VMSType.subclass = VMSTypeSub
# end class VMSTypeSub


class TEMPLATEType34Sub(TemplatedType, supermod.TEMPLATEType34):
    def __init__(self, VCENTER_CCR_REF=None, VCENTER_DS_REF=None, VCENTER_HOST=None, VCENTER_INSTANCE_ID=None, VCENTER_NAME=None, VCENTER_PASSWORD=None, VCENTER_RESOURCE_POOL_INFO=None, VCENTER_USER=None, VCENTER_VERSION=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType34Sub, self).__init__(VCENTER_CCR_REF, VCENTER_DS_REF, VCENTER_HOST, VCENTER_INSTANCE_ID, VCENTER_NAME, VCENTER_PASSWORD, VCENTER_RESOURCE_POOL_INFO, VCENTER_USER, VCENTER_VERSION, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType34.subclass = TEMPLATEType34Sub
# end class TEMPLATEType34Sub


class MONITORINGTypeSub(TemplatedType, supermod.MONITORINGType):
    def __init__(self, TIMESTAMP=None, ID=None, CAPACITY=None, SYSTEM=None, NUMA_NODE=None, **kwargs_):
        super(MONITORINGTypeSub, self).__init__(TIMESTAMP, ID, CAPACITY, SYSTEM, NUMA_NODE,  **kwargs_)
supermod.MONITORINGType.subclass = MONITORINGTypeSub
# end class MONITORINGTypeSub


class CAPACITYTypeSub(TemplatedType, supermod.CAPACITYType):
    def __init__(self, FREE_CPU=None, FREE_MEMORY=None, USED_CPU=None, USED_MEMORY=None, **kwargs_):
        super(CAPACITYTypeSub, self).__init__(FREE_CPU, FREE_MEMORY, USED_CPU, USED_MEMORY,  **kwargs_)
supermod.CAPACITYType.subclass = CAPACITYTypeSub
# end class CAPACITYTypeSub


class SYSTEMTypeSub(TemplatedType, supermod.SYSTEMType):
    def __init__(self, NETRX=None, NETTX=None, **kwargs_):
        super(SYSTEMTypeSub, self).__init__(NETRX, NETTX,  **kwargs_)
supermod.SYSTEMType.subclass = SYSTEMTypeSub
# end class SYSTEMTypeSub


class NUMA_NODETypeSub(TemplatedType, supermod.NUMA_NODEType):
    def __init__(self, HUGEPAGE=None, MEMORY=None, NODE_ID=None, **kwargs_):
        super(NUMA_NODETypeSub, self).__init__(HUGEPAGE, MEMORY, NODE_ID,  **kwargs_)
supermod.NUMA_NODEType.subclass = NUMA_NODETypeSub
# end class NUMA_NODETypeSub


class HUGEPAGEType35Sub(TemplatedType, supermod.HUGEPAGEType35):
    def __init__(self, FREE=None, SIZE=None, **kwargs_):
        super(HUGEPAGEType35Sub, self).__init__(FREE, SIZE,  **kwargs_)
supermod.HUGEPAGEType35.subclass = HUGEPAGEType35Sub
# end class HUGEPAGEType35Sub


class MEMORYType36Sub(TemplatedType, supermod.MEMORYType36):
    def __init__(self, FREE=None, USED=None, **kwargs_):
        super(MEMORYType36Sub, self).__init__(FREE, USED,  **kwargs_)
supermod.MEMORYType36.subclass = MEMORYType36Sub
# end class MEMORYType36Sub


class LOCKType37Sub(TemplatedType, supermod.LOCKType37):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType37Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType37.subclass = LOCKType37Sub
# end class LOCKType37Sub


class PERMISSIONSType38Sub(TemplatedType, supermod.PERMISSIONSType38):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType38Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType38.subclass = PERMISSIONSType38Sub
# end class PERMISSIONSType38Sub


class TEMPLATEType39Sub(TemplatedType, supermod.TEMPLATEType39):
    def __init__(self, VCENTER_IMPORTED=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType39Sub, self).__init__(VCENTER_IMPORTED, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType39.subclass = TEMPLATEType39Sub
# end class TEMPLATEType39Sub


class SNAPSHOTSType40Sub(TemplatedType, supermod.SNAPSHOTSType40):
    def __init__(self, ALLOW_ORPHANS=None, CURRENT_BASE=None, NEXT_SNAPSHOT=None, SNAPSHOT=None, **kwargs_):
        super(SNAPSHOTSType40Sub, self).__init__(ALLOW_ORPHANS, CURRENT_BASE, NEXT_SNAPSHOT, SNAPSHOT,  **kwargs_)
supermod.SNAPSHOTSType40.subclass = SNAPSHOTSType40Sub
# end class SNAPSHOTSType40Sub


class SNAPSHOTType41Sub(TemplatedType, supermod.SNAPSHOTType41):
    def __init__(self, CHILDREN=None, ACTIVE=None, DATE=None, ID=None, NAME=None, PARENT=None, SIZE=None, **kwargs_):
        super(SNAPSHOTType41Sub, self).__init__(CHILDREN, ACTIVE, DATE, ID, NAME, PARENT, SIZE,  **kwargs_)
supermod.SNAPSHOTType41.subclass = SNAPSHOTType41Sub
# end class SNAPSHOTType41Sub


class BACKUP_INCREMENTSTypeSub(TemplatedType, supermod.BACKUP_INCREMENTSType):
    def __init__(self, INCREMENT=None, **kwargs_):
        super(BACKUP_INCREMENTSTypeSub, self).__init__(INCREMENT,  **kwargs_)
supermod.BACKUP_INCREMENTSType.subclass = BACKUP_INCREMENTSTypeSub
# end class BACKUP_INCREMENTSTypeSub


class INCREMENTTypeSub(TemplatedType, supermod.INCREMENTType):
    def __init__(self, DATE=None, ID=None, PARENT_ID=None, SIZE=None, SOURCE=None, TYPE=None, **kwargs_):
        super(INCREMENTTypeSub, self).__init__(DATE, ID, PARENT_ID, SIZE, SOURCE, TYPE,  **kwargs_)
supermod.INCREMENTType.subclass = INCREMENTTypeSub
# end class INCREMENTTypeSub


class LOCKType42Sub(TemplatedType, supermod.LOCKType42):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType42Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType42.subclass = LOCKType42Sub
# end class LOCKType42Sub


class PERMISSIONSType43Sub(TemplatedType, supermod.PERMISSIONSType43):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType43Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType43.subclass = PERMISSIONSType43Sub
# end class PERMISSIONSType43Sub


class MARKETPLACEAPPSTypeSub(TemplatedType, supermod.MARKETPLACEAPPSType):
    def __init__(self, ID=None, **kwargs_):
        super(MARKETPLACEAPPSTypeSub, self).__init__(ID,  **kwargs_)
supermod.MARKETPLACEAPPSType.subclass = MARKETPLACEAPPSTypeSub
# end class MARKETPLACEAPPSTypeSub


class PERMISSIONSType44Sub(TemplatedType, supermod.PERMISSIONSType44):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType44Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType44.subclass = PERMISSIONSType44Sub
# end class PERMISSIONSType44Sub


class MONITORINGType45Sub(TemplatedType, supermod.MONITORINGType45):
    def __init__(self, CPU=None, DISKRDBYTES=None, DISKRDIOPS=None, DISKWRBYTES=None, DISKWRIOPS=None, DISK_SIZE=None, ID=None, MEMORY=None, NETRX=None, NETTX=None, TIMESTAMP=None, VCENTER_ESX_HOST=None, VCENTER_GUEST_STATE=None, VCENTER_RP_NAME=None, VCENTER_VMWARETOOLS_RUNNING_STATUS=None, VCENTER_VMWARETOOLS_VERSION=None, VCENTER_VMWARETOOLS_VERSION_STATUS=None, VCENTER_VM_NAME=None, **kwargs_):
        super(MONITORINGType45Sub, self).__init__(CPU, DISKRDBYTES, DISKRDIOPS, DISKWRBYTES, DISKWRIOPS, DISK_SIZE, ID, MEMORY, NETRX, NETTX, TIMESTAMP, VCENTER_ESX_HOST, VCENTER_GUEST_STATE, VCENTER_RP_NAME, VCENTER_VMWARETOOLS_RUNNING_STATUS, VCENTER_VMWARETOOLS_VERSION, VCENTER_VMWARETOOLS_VERSION_STATUS, VCENTER_VM_NAME,  **kwargs_)
supermod.MONITORINGType45.subclass = MONITORINGType45Sub
# end class MONITORINGType45Sub


class DISK_SIZETypeSub(TemplatedType, supermod.DISK_SIZEType):
    def __init__(self, ID=None, SIZE=None, **kwargs_):
        super(DISK_SIZETypeSub, self).__init__(ID, SIZE,  **kwargs_)
supermod.DISK_SIZEType.subclass = DISK_SIZETypeSub
# end class DISK_SIZETypeSub


class AUTH_MADTypeSub(TemplatedType, supermod.AUTH_MADType):
    def __init__(self, AUTHN=None, EXECUTABLE=None, **kwargs_):
        super(AUTH_MADTypeSub, self).__init__(AUTHN, EXECUTABLE,  **kwargs_)
supermod.AUTH_MADType.subclass = AUTH_MADTypeSub
# end class AUTH_MADTypeSub


class AUTH_MAD_CONFTypeSub(TemplatedType, supermod.AUTH_MAD_CONFType):
    def __init__(self, DRIVER_MANAGED_GROUPS=None, DRIVER_MANAGED_GROUP_ADMIN=None, MAX_TOKEN_TIME=None, NAME=None, PASSWORD_CHANGE=None, PASSWORD_REQUIRED=None, **kwargs_):
        super(AUTH_MAD_CONFTypeSub, self).__init__(DRIVER_MANAGED_GROUPS, DRIVER_MANAGED_GROUP_ADMIN, MAX_TOKEN_TIME, NAME, PASSWORD_CHANGE, PASSWORD_REQUIRED,  **kwargs_)
supermod.AUTH_MAD_CONFType.subclass = AUTH_MAD_CONFTypeSub
# end class AUTH_MAD_CONFTypeSub


class DATASTORE_MADTypeSub(TemplatedType, supermod.DATASTORE_MADType):
    def __init__(self, ARGUMENTS=None, EXECUTABLE=None, **kwargs_):
        super(DATASTORE_MADTypeSub, self).__init__(ARGUMENTS, EXECUTABLE,  **kwargs_)
supermod.DATASTORE_MADType.subclass = DATASTORE_MADTypeSub
# end class DATASTORE_MADTypeSub


class DBTypeSub(TemplatedType, supermod.DBType):
    def __init__(self, BACKEND=None, COMPARE_BINARY=None, CONNECTIONS=None, DB_NAME=None, PASSWD=None, PORT=None, SERVER=None, USER=None, TIMEOUT=None, **kwargs_):
        super(DBTypeSub, self).__init__(BACKEND, COMPARE_BINARY, CONNECTIONS, DB_NAME, PASSWD, PORT, SERVER, USER, TIMEOUT,  **kwargs_)
supermod.DBType.subclass = DBTypeSub
# end class DBTypeSub


class DEFAULT_COSTTypeSub(TemplatedType, supermod.DEFAULT_COSTType):
    def __init__(self, CPU_COST=None, DISK_COST=None, MEMORY_COST=None, **kwargs_):
        super(DEFAULT_COSTTypeSub, self).__init__(CPU_COST, DISK_COST, MEMORY_COST,  **kwargs_)
supermod.DEFAULT_COSTType.subclass = DEFAULT_COSTTypeSub
# end class DEFAULT_COSTTypeSub


class DS_MAD_CONFTypeSub(TemplatedType, supermod.DS_MAD_CONFType):
    def __init__(self, MARKETPLACE_ACTIONS=None, NAME=None, PERSISTENT_ONLY=None, REQUIRED_ATTRS=None, **kwargs_):
        super(DS_MAD_CONFTypeSub, self).__init__(MARKETPLACE_ACTIONS, NAME, PERSISTENT_ONLY, REQUIRED_ATTRS,  **kwargs_)
supermod.DS_MAD_CONFType.subclass = DS_MAD_CONFTypeSub
# end class DS_MAD_CONFTypeSub


class FEDERATIONTypeSub(TemplatedType, supermod.FEDERATIONType):
    def __init__(self, MASTER_ONED=None, MODE=None, SERVER_ID=None, ZONE_ID=None, **kwargs_):
        super(FEDERATIONTypeSub, self).__init__(MASTER_ONED, MODE, SERVER_ID, ZONE_ID,  **kwargs_)
supermod.FEDERATIONType.subclass = FEDERATIONTypeSub
# end class FEDERATIONTypeSub


class HM_MADTypeSub(TemplatedType, supermod.HM_MADType):
    def __init__(self, ARGUMENTS=None, EXECUTABLE=None, **kwargs_):
        super(HM_MADTypeSub, self).__init__(ARGUMENTS, EXECUTABLE,  **kwargs_)
supermod.HM_MADType.subclass = HM_MADTypeSub
# end class HM_MADTypeSub


class HOOK_LOG_CONFTypeSub(TemplatedType, supermod.HOOK_LOG_CONFType):
    def __init__(self, LOG_RETENTION=None, **kwargs_):
        super(HOOK_LOG_CONFTypeSub, self).__init__(LOG_RETENTION,  **kwargs_)
supermod.HOOK_LOG_CONFType.subclass = HOOK_LOG_CONFTypeSub
# end class HOOK_LOG_CONFTypeSub


class IM_MADTypeSub(TemplatedType, supermod.IM_MADType):
    def __init__(self, ARGUMENTS=None, EXECUTABLE=None, NAME=None, THREADS=None, **kwargs_):
        super(IM_MADTypeSub, self).__init__(ARGUMENTS, EXECUTABLE, NAME, THREADS,  **kwargs_)
supermod.IM_MADType.subclass = IM_MADTypeSub
# end class IM_MADTypeSub


class IPAM_MADTypeSub(TemplatedType, supermod.IPAM_MADType):
    def __init__(self, ARGUMENTS=None, EXECUTABLE=None, **kwargs_):
        super(IPAM_MADTypeSub, self).__init__(ARGUMENTS, EXECUTABLE,  **kwargs_)
supermod.IPAM_MADType.subclass = IPAM_MADTypeSub
# end class IPAM_MADTypeSub


class LOGTypeSub(TemplatedType, supermod.LOGType):
    def __init__(self, DEBUG_LEVEL=None, SYSTEM=None, USE_VMS_LOCATION=None, **kwargs_):
        super(LOGTypeSub, self).__init__(DEBUG_LEVEL, SYSTEM, USE_VMS_LOCATION,  **kwargs_)
supermod.LOGType.subclass = LOGTypeSub
# end class LOGTypeSub


class MARKET_MADTypeSub(TemplatedType, supermod.MARKET_MADType):
    def __init__(self, ARGUMENTS=None, EXECUTABLE=None, **kwargs_):
        super(MARKET_MADTypeSub, self).__init__(ARGUMENTS, EXECUTABLE,  **kwargs_)
supermod.MARKET_MADType.subclass = MARKET_MADTypeSub
# end class MARKET_MADTypeSub


class MARKET_MAD_CONFTypeSub(TemplatedType, supermod.MARKET_MAD_CONFType):
    def __init__(self, APP_ACTIONS=None, NAME=None, PUBLIC=None, REQUIRED_ATTRS=None, SUNSTONE_NAME=None, **kwargs_):
        super(MARKET_MAD_CONFTypeSub, self).__init__(APP_ACTIONS, NAME, PUBLIC, REQUIRED_ATTRS, SUNSTONE_NAME,  **kwargs_)
supermod.MARKET_MAD_CONFType.subclass = MARKET_MAD_CONFTypeSub
# end class MARKET_MAD_CONFTypeSub


class RAFTTypeSub(TemplatedType, supermod.RAFTType):
    def __init__(self, BROADCAST_TIMEOUT_MS=None, ELECTION_TIMEOUT_MS=None, LIMIT_PURGE=None, LOG_PURGE_TIMEOUT=None, LOG_RETENTION=None, XMLRPC_TIMEOUT_MS=None, **kwargs_):
        super(RAFTTypeSub, self).__init__(BROADCAST_TIMEOUT_MS, ELECTION_TIMEOUT_MS, LIMIT_PURGE, LOG_PURGE_TIMEOUT, LOG_RETENTION, XMLRPC_TIMEOUT_MS,  **kwargs_)
supermod.RAFTType.subclass = RAFTTypeSub
# end class RAFTTypeSub


class TM_MADTypeSub(TemplatedType, supermod.TM_MADType):
    def __init__(self, ARGUMENTS=None, EXECUTABLE=None, **kwargs_):
        super(TM_MADTypeSub, self).__init__(ARGUMENTS, EXECUTABLE,  **kwargs_)
supermod.TM_MADType.subclass = TM_MADTypeSub
# end class TM_MADTypeSub


class TM_MAD_CONFTypeSub(TemplatedType, supermod.TM_MAD_CONFType):
    def __init__(self, ALLOW_ORPHANS=None, CLONE_TARGET=None, CLONE_TARGET_SHARED=None, CLONE_TARGET_SSH=None, DISK_TYPE=None, DISK_TYPE_SHARED=None, DISK_TYPE_SSH=None, DRIVER=None, DS_MIGRATE=None, LN_TARGET=None, LN_TARGET_SHARED=None, LN_TARGET_SSH=None, NAME=None, SHARED=None, TM_MAD_SYSTEM=None, **kwargs_):
        super(TM_MAD_CONFTypeSub, self).__init__(ALLOW_ORPHANS, CLONE_TARGET, CLONE_TARGET_SHARED, CLONE_TARGET_SSH, DISK_TYPE, DISK_TYPE_SHARED, DISK_TYPE_SSH, DRIVER, DS_MIGRATE, LN_TARGET, LN_TARGET_SHARED, LN_TARGET_SSH, NAME, SHARED, TM_MAD_SYSTEM,  **kwargs_)
supermod.TM_MAD_CONFType.subclass = TM_MAD_CONFTypeSub
# end class TM_MAD_CONFTypeSub


class VLAN_IDSTypeSub(TemplatedType, supermod.VLAN_IDSType):
    def __init__(self, RESERVED=None, START=None, **kwargs_):
        super(VLAN_IDSTypeSub, self).__init__(RESERVED, START,  **kwargs_)
supermod.VLAN_IDSType.subclass = VLAN_IDSTypeSub
# end class VLAN_IDSTypeSub


class VM_MADTypeSub(TemplatedType, supermod.VM_MADType):
    def __init__(self, ARGUMENTS=None, DEFAULT=None, EXECUTABLE=None, IMPORTED_VMS_ACTIONS=None, NAME=None, SUNSTONE_NAME=None, TYPE=None, KEEP_SNAPSHOTS=None, COLD_NIC_ATTACH=None, DS_LIVE_MIGRATION=None, LIVE_RESIZE=None, **kwargs_):
        super(VM_MADTypeSub, self).__init__(ARGUMENTS, DEFAULT, EXECUTABLE, IMPORTED_VMS_ACTIONS, NAME, SUNSTONE_NAME, TYPE, KEEP_SNAPSHOTS, COLD_NIC_ATTACH, DS_LIVE_MIGRATION, LIVE_RESIZE,  **kwargs_)
supermod.VM_MADType.subclass = VM_MADTypeSub
# end class VM_MADTypeSub


class VNC_PORTSTypeSub(TemplatedType, supermod.VNC_PORTSType):
    def __init__(self, RESERVED=None, START=None, **kwargs_):
        super(VNC_PORTSTypeSub, self).__init__(RESERVED, START,  **kwargs_)
supermod.VNC_PORTSType.subclass = VNC_PORTSTypeSub
# end class VNC_PORTSTypeSub


class VN_MAD_CONFTypeSub(TemplatedType, supermod.VN_MAD_CONFType):
    def __init__(self, BRIDGE_TYPE=None, NAME=None, **kwargs_):
        super(VN_MAD_CONFTypeSub, self).__init__(BRIDGE_TYPE, NAME,  **kwargs_)
supermod.VN_MAD_CONFType.subclass = VN_MAD_CONFTypeSub
# end class VN_MAD_CONFTypeSub


class VXLAN_IDSTypeSub(TemplatedType, supermod.VXLAN_IDSType):
    def __init__(self, START=None, **kwargs_):
        super(VXLAN_IDSTypeSub, self).__init__(START,  **kwargs_)
supermod.VXLAN_IDSType.subclass = VXLAN_IDSTypeSub
# end class VXLAN_IDSTypeSub


class PERMISSIONSType46Sub(TemplatedType, supermod.PERMISSIONSType46):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType46Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType46.subclass = PERMISSIONSType46Sub
# end class PERMISSIONSType46Sub


class UPDATED_VMSTypeSub(TemplatedType, supermod.UPDATED_VMSType):
    def __init__(self, ID=None, **kwargs_):
        super(UPDATED_VMSTypeSub, self).__init__(ID,  **kwargs_)
supermod.UPDATED_VMSType.subclass = UPDATED_VMSTypeSub
# end class UPDATED_VMSTypeSub


class OUTDATED_VMSTypeSub(TemplatedType, supermod.OUTDATED_VMSType):
    def __init__(self, ID=None, **kwargs_):
        super(OUTDATED_VMSTypeSub, self).__init__(ID,  **kwargs_)
supermod.OUTDATED_VMSType.subclass = OUTDATED_VMSTypeSub
# end class OUTDATED_VMSTypeSub


class UPDATING_VMSTypeSub(TemplatedType, supermod.UPDATING_VMSType):
    def __init__(self, ID=None, **kwargs_):
        super(UPDATING_VMSTypeSub, self).__init__(ID,  **kwargs_)
supermod.UPDATING_VMSType.subclass = UPDATING_VMSTypeSub
# end class UPDATING_VMSTypeSub


class ERROR_VMSTypeSub(TemplatedType, supermod.ERROR_VMSType):
    def __init__(self, ID=None, **kwargs_):
        super(ERROR_VMSTypeSub, self).__init__(ID,  **kwargs_)
supermod.ERROR_VMSType.subclass = ERROR_VMSTypeSub
# end class ERROR_VMSTypeSub


class TEMPLATEType47Sub(TemplatedType, supermod.TEMPLATEType47):
    def __init__(self, DESCRIPTION=None, RULE=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType47Sub, self).__init__(DESCRIPTION, RULE, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType47.subclass = TEMPLATEType47Sub
# end class TEMPLATEType47Sub


class RULETypeSub(TemplatedType, supermod.RULEType):
    def __init__(self, PROTOCOL=None, RULE_TYPE=None, **kwargs_):
        super(RULETypeSub, self).__init__(PROTOCOL, RULE_TYPE,  **kwargs_)
supermod.RULEType.subclass = RULETypeSub
# end class RULETypeSub


class SHOWBACKTypeSub(TemplatedType, supermod.SHOWBACKType):
    def __init__(self, VMID=None, VMNAME=None, UID=None, GID=None, UNAME=None, GNAME=None, YEAR=None, MONTH=None, CPU_COST=None, MEMORY_COST=None, DISK_COST=None, TOTAL_COST=None, HOURS=None, RHOURS=None, **kwargs_):
        super(SHOWBACKTypeSub, self).__init__(VMID, VMNAME, UID, GID, UNAME, GNAME, YEAR, MONTH, CPU_COST, MEMORY_COST, DISK_COST, TOTAL_COST, HOURS, RHOURS,  **kwargs_)
supermod.SHOWBACKType.subclass = SHOWBACKTypeSub
# end class SHOWBACKTypeSub


class USERTypeSub(TemplatedType, supermod.USERType):
    def __init__(self, ID=None, GID=None, GROUPS=None, GNAME=None, NAME=None, PASSWORD=None, AUTH_DRIVER=None, ENABLED=None, LOGIN_TOKEN=None, TEMPLATE=None, **kwargs_):
        super(USERTypeSub, self).__init__(ID, GID, GROUPS, GNAME, NAME, PASSWORD, AUTH_DRIVER, ENABLED, LOGIN_TOKEN, TEMPLATE,  **kwargs_)
supermod.USERType.subclass = USERTypeSub
# end class USERTypeSub


class GROUPSTypeSub(TemplatedType, supermod.GROUPSType):
    def __init__(self, ID=None, **kwargs_):
        super(GROUPSTypeSub, self).__init__(ID,  **kwargs_)
supermod.GROUPSType.subclass = GROUPSTypeSub
# end class GROUPSTypeSub


class LOGIN_TOKENTypeSub(TemplatedType, supermod.LOGIN_TOKENType):
    def __init__(self, TOKEN=None, EXPIRATION_TIME=None, EGID=None, **kwargs_):
        super(LOGIN_TOKENTypeSub, self).__init__(TOKEN, EXPIRATION_TIME, EGID,  **kwargs_)
supermod.LOGIN_TOKENType.subclass = LOGIN_TOKENTypeSub
# end class LOGIN_TOKENTypeSub


class QUOTASType48Sub(TemplatedType, supermod.QUOTASType48):
    def __init__(self, ID=None, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(QUOTASType48Sub, self).__init__(ID, DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.QUOTASType48.subclass = QUOTASType48Sub
# end class QUOTASType48Sub


class DATASTORE_QUOTAType49Sub(TemplatedType, supermod.DATASTORE_QUOTAType49):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType49Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType49.subclass = DATASTORE_QUOTAType49Sub
# end class DATASTORE_QUOTAType49Sub


class DATASTOREType50Sub(TemplatedType, supermod.DATASTOREType50):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType50Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType50.subclass = DATASTOREType50Sub
# end class DATASTOREType50Sub


class NETWORK_QUOTAType51Sub(TemplatedType, supermod.NETWORK_QUOTAType51):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType51Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType51.subclass = NETWORK_QUOTAType51Sub
# end class NETWORK_QUOTAType51Sub


class NETWORKType52Sub(TemplatedType, supermod.NETWORKType52):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType52Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType52.subclass = NETWORKType52Sub
# end class NETWORKType52Sub


class VM_QUOTAType53Sub(TemplatedType, supermod.VM_QUOTAType53):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType53Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType53.subclass = VM_QUOTAType53Sub
# end class VM_QUOTAType53Sub


class VMType54Sub(TemplatedType, supermod.VMType54):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType54Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType54.subclass = VMType54Sub
# end class VMType54Sub


class IMAGE_QUOTAType55Sub(TemplatedType, supermod.IMAGE_QUOTAType55):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType55Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType55.subclass = IMAGE_QUOTAType55Sub
# end class IMAGE_QUOTAType55Sub


class IMAGEType56Sub(TemplatedType, supermod.IMAGEType56):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType56Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType56.subclass = IMAGEType56Sub
# end class IMAGEType56Sub


class DEFAULT_USER_QUOTASTypeSub(TemplatedType, supermod.DEFAULT_USER_QUOTASType):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(DEFAULT_USER_QUOTASTypeSub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.DEFAULT_USER_QUOTASType.subclass = DEFAULT_USER_QUOTASTypeSub
# end class DEFAULT_USER_QUOTASTypeSub


class DATASTORE_QUOTAType57Sub(TemplatedType, supermod.DATASTORE_QUOTAType57):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType57Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType57.subclass = DATASTORE_QUOTAType57Sub
# end class DATASTORE_QUOTAType57Sub


class DATASTOREType58Sub(TemplatedType, supermod.DATASTOREType58):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType58Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType58.subclass = DATASTOREType58Sub
# end class DATASTOREType58Sub


class NETWORK_QUOTAType59Sub(TemplatedType, supermod.NETWORK_QUOTAType59):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType59Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType59.subclass = NETWORK_QUOTAType59Sub
# end class NETWORK_QUOTAType59Sub


class NETWORKType60Sub(TemplatedType, supermod.NETWORKType60):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType60Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType60.subclass = NETWORKType60Sub
# end class NETWORKType60Sub


class VM_QUOTAType61Sub(TemplatedType, supermod.VM_QUOTAType61):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType61Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType61.subclass = VM_QUOTAType61Sub
# end class VM_QUOTAType61Sub


class VMType62Sub(TemplatedType, supermod.VMType62):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType62Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType62.subclass = VMType62Sub
# end class VMType62Sub


class IMAGE_QUOTAType63Sub(TemplatedType, supermod.IMAGE_QUOTAType63):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType63Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType63.subclass = IMAGE_QUOTAType63Sub
# end class IMAGE_QUOTAType63Sub


class IMAGEType64Sub(TemplatedType, supermod.IMAGEType64):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType64Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType64.subclass = IMAGEType64Sub
# end class IMAGEType64Sub


class GROUPSType65Sub(TemplatedType, supermod.GROUPSType65):
    def __init__(self, ID=None, **kwargs_):
        super(GROUPSType65Sub, self).__init__(ID,  **kwargs_)
supermod.GROUPSType65.subclass = GROUPSType65Sub
# end class GROUPSType65Sub


class LOGIN_TOKENType66Sub(TemplatedType, supermod.LOGIN_TOKENType66):
    def __init__(self, TOKEN=None, EXPIRATION_TIME=None, EGID=None, **kwargs_):
        super(LOGIN_TOKENType66Sub, self).__init__(TOKEN, EXPIRATION_TIME, EGID,  **kwargs_)
supermod.LOGIN_TOKENType66.subclass = LOGIN_TOKENType66Sub
# end class LOGIN_TOKENType66Sub


class DATASTORE_QUOTAType67Sub(TemplatedType, supermod.DATASTORE_QUOTAType67):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType67Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType67.subclass = DATASTORE_QUOTAType67Sub
# end class DATASTORE_QUOTAType67Sub


class DATASTOREType68Sub(TemplatedType, supermod.DATASTOREType68):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType68Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType68.subclass = DATASTOREType68Sub
# end class DATASTOREType68Sub


class NETWORK_QUOTAType69Sub(TemplatedType, supermod.NETWORK_QUOTAType69):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType69Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType69.subclass = NETWORK_QUOTAType69Sub
# end class NETWORK_QUOTAType69Sub


class NETWORKType70Sub(TemplatedType, supermod.NETWORKType70):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType70Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType70.subclass = NETWORKType70Sub
# end class NETWORKType70Sub


class VM_QUOTAType71Sub(TemplatedType, supermod.VM_QUOTAType71):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType71Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType71.subclass = VM_QUOTAType71Sub
# end class VM_QUOTAType71Sub


class VMType72Sub(TemplatedType, supermod.VMType72):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType72Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType72.subclass = VMType72Sub
# end class VMType72Sub


class IMAGE_QUOTAType73Sub(TemplatedType, supermod.IMAGE_QUOTAType73):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType73Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType73.subclass = IMAGE_QUOTAType73Sub
# end class IMAGE_QUOTAType73Sub


class IMAGEType74Sub(TemplatedType, supermod.IMAGEType74):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType74Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType74.subclass = IMAGEType74Sub
# end class IMAGEType74Sub


class DEFAULT_USER_QUOTASType75Sub(TemplatedType, supermod.DEFAULT_USER_QUOTASType75):
    def __init__(self, DATASTORE_QUOTA=None, NETWORK_QUOTA=None, VM_QUOTA=None, IMAGE_QUOTA=None, **kwargs_):
        super(DEFAULT_USER_QUOTASType75Sub, self).__init__(DATASTORE_QUOTA, NETWORK_QUOTA, VM_QUOTA, IMAGE_QUOTA,  **kwargs_)
supermod.DEFAULT_USER_QUOTASType75.subclass = DEFAULT_USER_QUOTASType75Sub
# end class DEFAULT_USER_QUOTASType75Sub


class DATASTORE_QUOTAType76Sub(TemplatedType, supermod.DATASTORE_QUOTAType76):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORE_QUOTAType76Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORE_QUOTAType76.subclass = DATASTORE_QUOTAType76Sub
# end class DATASTORE_QUOTAType76Sub


class DATASTOREType77Sub(TemplatedType, supermod.DATASTOREType77):
    def __init__(self, ID=None, IMAGES=None, IMAGES_USED=None, SIZE=None, SIZE_USED=None, **kwargs_):
        super(DATASTOREType77Sub, self).__init__(ID, IMAGES, IMAGES_USED, SIZE, SIZE_USED,  **kwargs_)
supermod.DATASTOREType77.subclass = DATASTOREType77Sub
# end class DATASTOREType77Sub


class NETWORK_QUOTAType78Sub(TemplatedType, supermod.NETWORK_QUOTAType78):
    def __init__(self, NETWORK=None, **kwargs_):
        super(NETWORK_QUOTAType78Sub, self).__init__(NETWORK,  **kwargs_)
supermod.NETWORK_QUOTAType78.subclass = NETWORK_QUOTAType78Sub
# end class NETWORK_QUOTAType78Sub


class NETWORKType79Sub(TemplatedType, supermod.NETWORKType79):
    def __init__(self, ID=None, LEASES=None, LEASES_USED=None, **kwargs_):
        super(NETWORKType79Sub, self).__init__(ID, LEASES, LEASES_USED,  **kwargs_)
supermod.NETWORKType79.subclass = NETWORKType79Sub
# end class NETWORKType79Sub


class VM_QUOTAType80Sub(TemplatedType, supermod.VM_QUOTAType80):
    def __init__(self, VM=None, **kwargs_):
        super(VM_QUOTAType80Sub, self).__init__(VM,  **kwargs_)
supermod.VM_QUOTAType80.subclass = VM_QUOTAType80Sub
# end class VM_QUOTAType80Sub


class VMType81Sub(TemplatedType, supermod.VMType81):
    def __init__(self, CPU=None, CPU_USED=None, MEMORY=None, MEMORY_USED=None, RUNNING_CPU=None, RUNNING_CPU_USED=None, RUNNING_MEMORY=None, RUNNING_MEMORY_USED=None, RUNNING_VMS=None, RUNNING_VMS_USED=None, SYSTEM_DISK_SIZE=None, SYSTEM_DISK_SIZE_USED=None, VMS=None, VMS_USED=None, **kwargs_):
        super(VMType81Sub, self).__init__(CPU, CPU_USED, MEMORY, MEMORY_USED, RUNNING_CPU, RUNNING_CPU_USED, RUNNING_MEMORY, RUNNING_MEMORY_USED, RUNNING_VMS, RUNNING_VMS_USED, SYSTEM_DISK_SIZE, SYSTEM_DISK_SIZE_USED, VMS, VMS_USED,  **kwargs_)
supermod.VMType81.subclass = VMType81Sub
# end class VMType81Sub


class IMAGE_QUOTAType82Sub(TemplatedType, supermod.IMAGE_QUOTAType82):
    def __init__(self, IMAGE=None, **kwargs_):
        super(IMAGE_QUOTAType82Sub, self).__init__(IMAGE,  **kwargs_)
supermod.IMAGE_QUOTAType82.subclass = IMAGE_QUOTAType82Sub
# end class IMAGE_QUOTAType82Sub


class IMAGEType83Sub(TemplatedType, supermod.IMAGEType83):
    def __init__(self, ID=None, RVMS=None, RVMS_USED=None, **kwargs_):
        super(IMAGEType83Sub, self).__init__(ID, RVMS, RVMS_USED,  **kwargs_)
supermod.IMAGEType83.subclass = IMAGEType83Sub
# end class IMAGEType83Sub


class GROUPSType84Sub(TemplatedType, supermod.GROUPSType84):
    def __init__(self, ID=None, **kwargs_):
        super(GROUPSType84Sub, self).__init__(ID,  **kwargs_)
supermod.GROUPSType84.subclass = GROUPSType84Sub
# end class GROUPSType84Sub


class CLUSTERSType85Sub(TemplatedType, supermod.CLUSTERSType85):
    def __init__(self, CLUSTER=None, **kwargs_):
        super(CLUSTERSType85Sub, self).__init__(CLUSTER,  **kwargs_)
supermod.CLUSTERSType85.subclass = CLUSTERSType85Sub
# end class CLUSTERSType85Sub


class CLUSTERTypeSub(TemplatedType, supermod.CLUSTERType):
    def __init__(self, ZONE_ID=None, CLUSTER_ID=None, **kwargs_):
        super(CLUSTERTypeSub, self).__init__(ZONE_ID, CLUSTER_ID,  **kwargs_)
supermod.CLUSTERType.subclass = CLUSTERTypeSub
# end class CLUSTERTypeSub


class HOSTSType86Sub(TemplatedType, supermod.HOSTSType86):
    def __init__(self, HOST=None, **kwargs_):
        super(HOSTSType86Sub, self).__init__(HOST,  **kwargs_)
supermod.HOSTSType86.subclass = HOSTSType86Sub
# end class HOSTSType86Sub


class HOSTTypeSub(TemplatedType, supermod.HOSTType):
    def __init__(self, ZONE_ID=None, HOST_ID=None, **kwargs_):
        super(HOSTTypeSub, self).__init__(ZONE_ID, HOST_ID,  **kwargs_)
supermod.HOSTType.subclass = HOSTTypeSub
# end class HOSTTypeSub


class DATASTORESType87Sub(TemplatedType, supermod.DATASTORESType87):
    def __init__(self, DATASTORE=None, **kwargs_):
        super(DATASTORESType87Sub, self).__init__(DATASTORE,  **kwargs_)
supermod.DATASTORESType87.subclass = DATASTORESType87Sub
# end class DATASTORESType87Sub


class DATASTOREType88Sub(TemplatedType, supermod.DATASTOREType88):
    def __init__(self, ZONE_ID=None, DATASTORE_ID=None, **kwargs_):
        super(DATASTOREType88Sub, self).__init__(ZONE_ID, DATASTORE_ID,  **kwargs_)
supermod.DATASTOREType88.subclass = DATASTOREType88Sub
# end class DATASTOREType88Sub


class VNETSType89Sub(TemplatedType, supermod.VNETSType89):
    def __init__(self, VNET=None, **kwargs_):
        super(VNETSType89Sub, self).__init__(VNET,  **kwargs_)
supermod.VNETSType89.subclass = VNETSType89Sub
# end class VNETSType89Sub


class VNETTypeSub(TemplatedType, supermod.VNETType):
    def __init__(self, ZONE_ID=None, VNET_ID=None, **kwargs_):
        super(VNETTypeSub, self).__init__(ZONE_ID, VNET_ID,  **kwargs_)
supermod.VNETType.subclass = VNETTypeSub
# end class VNETTypeSub


class PERMISSIONSType90Sub(TemplatedType, supermod.PERMISSIONSType90):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType90Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType90.subclass = PERMISSIONSType90Sub
# end class PERMISSIONSType90Sub


class LOCKType91Sub(TemplatedType, supermod.LOCKType91):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType91Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType91.subclass = LOCKType91Sub
# end class LOCKType91Sub


class ROLESTypeSub(TemplatedType, supermod.ROLESType):
    def __init__(self, ROLE=None, **kwargs_):
        super(ROLESTypeSub, self).__init__(ROLE,  **kwargs_)
supermod.ROLESType.subclass = ROLESTypeSub
# end class ROLESTypeSub


class ROLETypeSub(TemplatedType, supermod.ROLEType):
    def __init__(self, HOST_AFFINED=None, HOST_ANTI_AFFINED=None, ID=None, NAME=None, POLICY=None, VMS=None, **kwargs_):
        super(ROLETypeSub, self).__init__(HOST_AFFINED, HOST_ANTI_AFFINED, ID, NAME, POLICY, VMS,  **kwargs_)
supermod.ROLEType.subclass = ROLETypeSub
# end class ROLETypeSub


class VMType92Sub(TemplatedType, supermod.VMType92):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, LAST_POLL=None, STATE=None, LCM_STATE=None, RESCHED=None, STIME=None, ETIME=None, DEPLOY_ID=None, TEMPLATE=None, MONITORING=None, USER_TEMPLATE=None, HISTORY_RECORDS=None, **kwargs_):
        super(VMType92Sub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, LAST_POLL, STATE, LCM_STATE, RESCHED, STIME, ETIME, DEPLOY_ID, TEMPLATE, MONITORING, USER_TEMPLATE, HISTORY_RECORDS,  **kwargs_)
supermod.VMType92.subclass = VMType92Sub
# end class VMType92Sub


class TEMPLATEType93Sub(TemplatedType, supermod.TEMPLATEType93):
    def __init__(self, CPU=None, MEMORY=None, VCPU=None, DISK=None, NIC=None, GRAPHICS=None, **kwargs_):
        super(TEMPLATEType93Sub, self).__init__(CPU, MEMORY, VCPU, DISK, NIC, GRAPHICS,  **kwargs_)
supermod.TEMPLATEType93.subclass = TEMPLATEType93Sub
# end class TEMPLATEType93Sub


class DISKTypeSub(TemplatedType, supermod.DISKType):
    def __init__(self, VCENTER_DS_REF=None, VCENTER_INSTANCE_ID=None, anytypeobjs_=None, **kwargs_):
        super(DISKTypeSub, self).__init__(VCENTER_DS_REF, VCENTER_INSTANCE_ID, anytypeobjs_,  **kwargs_)
supermod.DISKType.subclass = DISKTypeSub
# end class DISKTypeSub


class NICTypeSub(TemplatedType, supermod.NICType):
    def __init__(self, anytypeobjs_=None, VCENTER_INSTANCE_ID=None, VCENTER_NET_REF=None, VCENTER_PORTGROUP_TYPE=None, **kwargs_):
        super(NICTypeSub, self).__init__(anytypeobjs_, VCENTER_INSTANCE_ID, VCENTER_NET_REF, VCENTER_PORTGROUP_TYPE,  **kwargs_)
supermod.NICType.subclass = NICTypeSub
# end class NICTypeSub


class MONITORINGType94Sub(TemplatedType, supermod.MONITORINGType94):
    def __init__(self, anytypeobjs_=None, **kwargs_):
        super(MONITORINGType94Sub, self).__init__(anytypeobjs_,  **kwargs_)
supermod.MONITORINGType94.subclass = MONITORINGType94Sub
# end class MONITORINGType94Sub


class USER_TEMPLATETypeSub(TemplatedType, supermod.USER_TEMPLATEType):
    def __init__(self, LABELS=None, ERROR=None, SCHED_MESSAGE=None, SCHED_RANK=None, SCHED_DS_RANK=None, SCHED_REQUIREMENTS=None, SCHED_DS_REQUIREMENTS=None, USER_PRIORITY=None, PUBLIC_CLOUD=None, SCHED_ACTION=None, anytypeobjs_=None, **kwargs_):
        super(USER_TEMPLATETypeSub, self).__init__(LABELS, ERROR, SCHED_MESSAGE, SCHED_RANK, SCHED_DS_RANK, SCHED_REQUIREMENTS, SCHED_DS_REQUIREMENTS, USER_PRIORITY, PUBLIC_CLOUD, SCHED_ACTION, anytypeobjs_,  **kwargs_)
supermod.USER_TEMPLATEType.subclass = USER_TEMPLATETypeSub
# end class USER_TEMPLATETypeSub


class PUBLIC_CLOUDTypeSub(TemplatedType, supermod.PUBLIC_CLOUDType):
    def __init__(self, anytypeobjs_=None, **kwargs_):
        super(PUBLIC_CLOUDTypeSub, self).__init__(anytypeobjs_,  **kwargs_)
supermod.PUBLIC_CLOUDType.subclass = PUBLIC_CLOUDTypeSub
# end class PUBLIC_CLOUDTypeSub


class SCHED_ACTIONTypeSub(TemplatedType, supermod.SCHED_ACTIONType):
    def __init__(self, anytypeobjs_=None, **kwargs_):
        super(SCHED_ACTIONTypeSub, self).__init__(anytypeobjs_,  **kwargs_)
supermod.SCHED_ACTIONType.subclass = SCHED_ACTIONTypeSub
# end class SCHED_ACTIONTypeSub


class HISTORY_RECORDSTypeSub(TemplatedType, supermod.HISTORY_RECORDSType):
    def __init__(self, HISTORY=None, **kwargs_):
        super(HISTORY_RECORDSTypeSub, self).__init__(HISTORY,  **kwargs_)
supermod.HISTORY_RECORDSType.subclass = HISTORY_RECORDSTypeSub
# end class HISTORY_RECORDSTypeSub


class HISTORYTypeSub(TemplatedType, supermod.HISTORYType):
    def __init__(self, OID=None, SEQ=None, HOSTNAME=None, HID=None, CID=None, DS_ID=None, VM_MAD=None, TM_MAD=None, ACTION=None, **kwargs_):
        super(HISTORYTypeSub, self).__init__(OID, SEQ, HOSTNAME, HID, CID, DS_ID, VM_MAD, TM_MAD, ACTION,  **kwargs_)
supermod.HISTORYType.subclass = HISTORYTypeSub
# end class HISTORYTypeSub


class LOCKType95Sub(TemplatedType, supermod.LOCKType95):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType95Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType95.subclass = LOCKType95Sub
# end class LOCKType95Sub


class PERMISSIONSType96Sub(TemplatedType, supermod.PERMISSIONSType96):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType96Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType96.subclass = PERMISSIONSType96Sub
# end class PERMISSIONSType96Sub


class TEMPLATEType97Sub(TemplatedType, supermod.TEMPLATEType97):
    def __init__(self, VCENTER_CCR_REF=None, VCENTER_INSTANCE_ID=None, VCENTER_TEMPLATE_REF=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType97Sub, self).__init__(VCENTER_CCR_REF, VCENTER_INSTANCE_ID, VCENTER_TEMPLATE_REF, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType97.subclass = TEMPLATEType97Sub
# end class TEMPLATEType97Sub


class MONITORINGType98Sub(TemplatedType, supermod.MONITORINGType98):
    def __init__(self, CPU=None, DISKRDBYTES=None, DISKRDIOPS=None, DISKWRBYTES=None, DISKWRIOPS=None, DISK_SIZE=None, ID=None, MEMORY=None, NETRX=None, NETTX=None, TIMESTAMP=None, VCENTER_ESX_HOST=None, VCENTER_GUEST_STATE=None, VCENTER_RP_NAME=None, VCENTER_VMWARETOOLS_RUNNING_STATUS=None, VCENTER_VMWARETOOLS_VERSION=None, VCENTER_VMWARETOOLS_VERSION_STATUS=None, VCENTER_VM_NAME=None, anytypeobjs_=None, **kwargs_):
        super(MONITORINGType98Sub, self).__init__(CPU, DISKRDBYTES, DISKRDIOPS, DISKWRBYTES, DISKWRIOPS, DISK_SIZE, ID, MEMORY, NETRX, NETTX, TIMESTAMP, VCENTER_ESX_HOST, VCENTER_GUEST_STATE, VCENTER_RP_NAME, VCENTER_VMWARETOOLS_RUNNING_STATUS, VCENTER_VMWARETOOLS_VERSION, VCENTER_VMWARETOOLS_VERSION_STATUS, VCENTER_VM_NAME, anytypeobjs_,  **kwargs_)
supermod.MONITORINGType98.subclass = MONITORINGType98Sub
# end class MONITORINGType98Sub


class DISK_SIZEType99Sub(TemplatedType, supermod.DISK_SIZEType99):
    def __init__(self, ID=None, SIZE=None, **kwargs_):
        super(DISK_SIZEType99Sub, self).__init__(ID, SIZE,  **kwargs_)
supermod.DISK_SIZEType99.subclass = DISK_SIZEType99Sub
# end class DISK_SIZEType99Sub


class TEMPLATEType100Sub(TemplatedType, supermod.TEMPLATEType100):
    def __init__(self, AUTOMATIC_DS_REQUIREMENTS=None, AUTOMATIC_NIC_REQUIREMENTS=None, AUTOMATIC_REQUIREMENTS=None, CLONING_TEMPLATE_ID=None, CONTEXT=None, CPU=None, CPU_COST=None, DISK=None, DISK_COST=None, EMULATOR=None, FEATURES=None, HYPERV_OPTIONS=None, GRAPHICS=None, VIDEO=None, IMPORTED=None, INPUT=None, MEMORY=None, MEMORY_COST=None, MEMORY_MAX=None, MEMORY_SLOTS=None, MEMORY_RESIZE_MODE=None, NIC=None, NIC_ALIAS=None, NIC_DEFAULT=None, NUMA_NODE=None, OS=None, PCI=None, RAW=None, SECURITY_GROUP_RULE=None, SNAPSHOT=None, SPICE_OPTIONS=None, SUBMIT_ON_HOLD=None, TEMPLATE_ID=None, TM_MAD_SYSTEM=None, TOPOLOGY=None, VCPU=None, VCPU_MAX=None, VMGROUP=None, VMID=None, VROUTER_ID=None, VROUTER_KEEPALIVED_ID=None, VROUTER_KEEPALIVED_PASSWORD=None, SCHED_ACTION=None, **kwargs_):
        super(TEMPLATEType100Sub, self).__init__(AUTOMATIC_DS_REQUIREMENTS, AUTOMATIC_NIC_REQUIREMENTS, AUTOMATIC_REQUIREMENTS, CLONING_TEMPLATE_ID, CONTEXT, CPU, CPU_COST, DISK, DISK_COST, EMULATOR, FEATURES, HYPERV_OPTIONS, GRAPHICS, VIDEO, IMPORTED, INPUT, MEMORY, MEMORY_COST, MEMORY_MAX, MEMORY_SLOTS, MEMORY_RESIZE_MODE, NIC, NIC_ALIAS, NIC_DEFAULT, NUMA_NODE, OS, PCI, RAW, SECURITY_GROUP_RULE, SNAPSHOT, SPICE_OPTIONS, SUBMIT_ON_HOLD, TEMPLATE_ID, TM_MAD_SYSTEM, TOPOLOGY, VCPU, VCPU_MAX, VMGROUP, VMID, VROUTER_ID, VROUTER_KEEPALIVED_ID, VROUTER_KEEPALIVED_PASSWORD, SCHED_ACTION,  **kwargs_)
supermod.TEMPLATEType100.subclass = TEMPLATEType100Sub
# end class TEMPLATEType100Sub


class DISKType101Sub(TemplatedType, supermod.DISKType101):
    def __init__(self, VCENTER_DS_REF=None, VCENTER_INSTANCE_ID=None, anytypeobjs_=None, **kwargs_):
        super(DISKType101Sub, self).__init__(VCENTER_DS_REF, VCENTER_INSTANCE_ID, anytypeobjs_,  **kwargs_)
supermod.DISKType101.subclass = DISKType101Sub
# end class DISKType101Sub


class VIDEOTypeSub(TemplatedType, supermod.VIDEOType):
    def __init__(self, TYPE=None, IOMMU=None, ATS=None, VRAM=None, RESOLUTION=None, **kwargs_):
        super(VIDEOTypeSub, self).__init__(TYPE, IOMMU, ATS, VRAM, RESOLUTION,  **kwargs_)
supermod.VIDEOType.subclass = VIDEOTypeSub
# end class VIDEOTypeSub


class NICType102Sub(TemplatedType, supermod.NICType102):
    def __init__(self, anytypeobjs_=None, VCENTER_INSTANCE_ID=None, VCENTER_NET_REF=None, VCENTER_PORTGROUP_TYPE=None, **kwargs_):
        super(NICType102Sub, self).__init__(anytypeobjs_, VCENTER_INSTANCE_ID, VCENTER_NET_REF, VCENTER_PORTGROUP_TYPE,  **kwargs_)
supermod.NICType102.subclass = NICType102Sub
# end class NICType102Sub


class NIC_ALIASTypeSub(TemplatedType, supermod.NIC_ALIASType):
    def __init__(self, ALIAS_ID=None, PARENT=None, PARENT_ID=None, anytypeobjs_=None, VCENTER_INSTANCE_ID=None, VCENTER_NET_REF=None, VCENTER_PORTGROUP_TYPE=None, **kwargs_):
        super(NIC_ALIASTypeSub, self).__init__(ALIAS_ID, PARENT, PARENT_ID, anytypeobjs_, VCENTER_INSTANCE_ID, VCENTER_NET_REF, VCENTER_PORTGROUP_TYPE,  **kwargs_)
supermod.NIC_ALIASType.subclass = NIC_ALIASTypeSub
# end class NIC_ALIASTypeSub


class SNAPSHOTType103Sub(TemplatedType, supermod.SNAPSHOTType103):
    def __init__(self, ACTION=None, ACTIVE=None, HYPERVISOR_ID=None, NAME=None, SNAPSHOT_ID=None, SYSTEM_DISK_SIZE=None, TIME=None, **kwargs_):
        super(SNAPSHOTType103Sub, self).__init__(ACTION, ACTIVE, HYPERVISOR_ID, NAME, SNAPSHOT_ID, SYSTEM_DISK_SIZE, TIME,  **kwargs_)
supermod.SNAPSHOTType103.subclass = SNAPSHOTType103Sub
# end class SNAPSHOTType103Sub


class USER_TEMPLATEType104Sub(TemplatedType, supermod.USER_TEMPLATEType104):
    def __init__(self, VCENTER_CCR_REF=None, VCENTER_DS_REF=None, VCENTER_INSTANCE_ID=None, anytypeobjs_=None, **kwargs_):
        super(USER_TEMPLATEType104Sub, self).__init__(VCENTER_CCR_REF, VCENTER_DS_REF, VCENTER_INSTANCE_ID, anytypeobjs_,  **kwargs_)
supermod.USER_TEMPLATEType104.subclass = USER_TEMPLATEType104Sub
# end class USER_TEMPLATEType104Sub


class HISTORY_RECORDSType105Sub(TemplatedType, supermod.HISTORY_RECORDSType105):
    def __init__(self, HISTORY=None, **kwargs_):
        super(HISTORY_RECORDSType105Sub, self).__init__(HISTORY,  **kwargs_)
supermod.HISTORY_RECORDSType105.subclass = HISTORY_RECORDSType105Sub
# end class HISTORY_RECORDSType105Sub


class HISTORYType106Sub(TemplatedType, supermod.HISTORYType106):
    def __init__(self, OID=None, SEQ=None, HOSTNAME=None, HID=None, CID=None, STIME=None, ETIME=None, VM_MAD=None, TM_MAD=None, DS_ID=None, PSTIME=None, PETIME=None, RSTIME=None, RETIME=None, ESTIME=None, EETIME=None, ACTION=None, UID=None, GID=None, REQUEST_ID=None, **kwargs_):
        super(HISTORYType106Sub, self).__init__(OID, SEQ, HOSTNAME, HID, CID, STIME, ETIME, VM_MAD, TM_MAD, DS_ID, PSTIME, PETIME, RSTIME, RETIME, ESTIME, EETIME, ACTION, UID, GID, REQUEST_ID,  **kwargs_)
supermod.HISTORYType106.subclass = HISTORYType106Sub
# end class HISTORYType106Sub


class SNAPSHOTSType107Sub(TemplatedType, supermod.SNAPSHOTSType107):
    def __init__(self, ALLOW_ORPHANS=None, CURRENT_BASE=None, DISK_ID=None, NEXT_SNAPSHOT=None, SNAPSHOT=None, **kwargs_):
        super(SNAPSHOTSType107Sub, self).__init__(ALLOW_ORPHANS, CURRENT_BASE, DISK_ID, NEXT_SNAPSHOT, SNAPSHOT,  **kwargs_)
supermod.SNAPSHOTSType107.subclass = SNAPSHOTSType107Sub
# end class SNAPSHOTSType107Sub


class SNAPSHOTType108Sub(TemplatedType, supermod.SNAPSHOTType108):
    def __init__(self, ACTIVE=None, CHILDREN=None, DATE=None, ID=None, NAME=None, PARENT=None, SIZE=None, **kwargs_):
        super(SNAPSHOTType108Sub, self).__init__(ACTIVE, CHILDREN, DATE, ID, NAME, PARENT, SIZE,  **kwargs_)
supermod.SNAPSHOTType108.subclass = SNAPSHOTType108Sub
# end class SNAPSHOTType108Sub


class BACKUPSType109Sub(TemplatedType, supermod.BACKUPSType109):
    def __init__(self, BACKUP_CONFIG=None, BACKUP_IDS=None, **kwargs_):
        super(BACKUPSType109Sub, self).__init__(BACKUP_CONFIG, BACKUP_IDS,  **kwargs_)
supermod.BACKUPSType109.subclass = BACKUPSType109Sub
# end class BACKUPSType109Sub


class BACKUP_CONFIGType110Sub(TemplatedType, supermod.BACKUP_CONFIGType110):
    def __init__(self, BACKUP_JOB_ID=None, BACKUP_VOLATILE=None, FS_FREEZE=None, INCREMENTAL_BACKUP_ID=None, INCREMENT_MODE=None, KEEP_LAST=None, LAST_BACKUP_ID=None, LAST_BACKUP_SIZE=None, LAST_DATASTORE_ID=None, LAST_INCREMENT_ID=None, MODE=None, **kwargs_):
        super(BACKUP_CONFIGType110Sub, self).__init__(BACKUP_JOB_ID, BACKUP_VOLATILE, FS_FREEZE, INCREMENTAL_BACKUP_ID, INCREMENT_MODE, KEEP_LAST, LAST_BACKUP_ID, LAST_BACKUP_SIZE, LAST_DATASTORE_ID, LAST_INCREMENT_ID, MODE,  **kwargs_)
supermod.BACKUP_CONFIGType110.subclass = BACKUP_CONFIGType110Sub
# end class BACKUP_CONFIGType110Sub


class VNETType111Sub(TemplatedType, supermod.VNETType111):
    def __init__(self, ID=None, UID=None, GID=None, UNAME=None, GNAME=None, NAME=None, PERMISSIONS=None, CLUSTERS=None, BRIDGE=None, BRIDGE_TYPE=None, STATE=None, PREV_STATE=None, PARENT_NETWORK_ID=None, VN_MAD=None, PHYDEV=None, VLAN_ID=None, OUTER_VLAN_ID=None, VLAN_ID_AUTOMATIC=None, OUTER_VLAN_ID_AUTOMATIC=None, USED_LEASES=None, VROUTERS=None, UPDATED_VMS=None, OUTDATED_VMS=None, UPDATING_VMS=None, ERROR_VMS=None, TEMPLATE=None, AR_POOL=None, **kwargs_):
        super(VNETType111Sub, self).__init__(ID, UID, GID, UNAME, GNAME, NAME, PERMISSIONS, CLUSTERS, BRIDGE, BRIDGE_TYPE, STATE, PREV_STATE, PARENT_NETWORK_ID, VN_MAD, PHYDEV, VLAN_ID, OUTER_VLAN_ID, VLAN_ID_AUTOMATIC, OUTER_VLAN_ID_AUTOMATIC, USED_LEASES, VROUTERS, UPDATED_VMS, OUTDATED_VMS, UPDATING_VMS, ERROR_VMS, TEMPLATE, AR_POOL,  **kwargs_)
supermod.VNETType111.subclass = VNETType111Sub
# end class VNETType111Sub


class PERMISSIONSType112Sub(TemplatedType, supermod.PERMISSIONSType112):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType112Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType112.subclass = PERMISSIONSType112Sub
# end class PERMISSIONSType112Sub


class CLUSTERSType113Sub(TemplatedType, supermod.CLUSTERSType113):
    def __init__(self, ID=None, **kwargs_):
        super(CLUSTERSType113Sub, self).__init__(ID,  **kwargs_)
supermod.CLUSTERSType113.subclass = CLUSTERSType113Sub
# end class CLUSTERSType113Sub


class VROUTERSTypeSub(TemplatedType, supermod.VROUTERSType):
    def __init__(self, ID=None, **kwargs_):
        super(VROUTERSTypeSub, self).__init__(ID,  **kwargs_)
supermod.VROUTERSType.subclass = VROUTERSTypeSub
# end class VROUTERSTypeSub


class UPDATED_VMSType114Sub(TemplatedType, supermod.UPDATED_VMSType114):
    def __init__(self, ID=None, **kwargs_):
        super(UPDATED_VMSType114Sub, self).__init__(ID,  **kwargs_)
supermod.UPDATED_VMSType114.subclass = UPDATED_VMSType114Sub
# end class UPDATED_VMSType114Sub


class OUTDATED_VMSType115Sub(TemplatedType, supermod.OUTDATED_VMSType115):
    def __init__(self, ID=None, **kwargs_):
        super(OUTDATED_VMSType115Sub, self).__init__(ID,  **kwargs_)
supermod.OUTDATED_VMSType115.subclass = OUTDATED_VMSType115Sub
# end class OUTDATED_VMSType115Sub


class UPDATING_VMSType116Sub(TemplatedType, supermod.UPDATING_VMSType116):
    def __init__(self, ID=None, **kwargs_):
        super(UPDATING_VMSType116Sub, self).__init__(ID,  **kwargs_)
supermod.UPDATING_VMSType116.subclass = UPDATING_VMSType116Sub
# end class UPDATING_VMSType116Sub


class ERROR_VMSType117Sub(TemplatedType, supermod.ERROR_VMSType117):
    def __init__(self, ID=None, **kwargs_):
        super(ERROR_VMSType117Sub, self).__init__(ID,  **kwargs_)
supermod.ERROR_VMSType117.subclass = ERROR_VMSType117Sub
# end class ERROR_VMSType117Sub


class AR_POOLTypeSub(TemplatedType, supermod.AR_POOLType):
    def __init__(self, AR=None, **kwargs_):
        super(AR_POOLTypeSub, self).__init__(AR,  **kwargs_)
supermod.AR_POOLType.subclass = AR_POOLTypeSub
# end class AR_POOLTypeSub


class ARTypeSub(TemplatedType, supermod.ARType):
    def __init__(self, ALLOCATED=None, AR_ID=None, GLOBAL_PREFIX=None, IP=None, MAC=None, PARENT_NETWORK_AR_ID=None, SIZE=None, TYPE=None, ULA_PREFIX=None, VN_MAD=None, **kwargs_):
        super(ARTypeSub, self).__init__(ALLOCATED, AR_ID, GLOBAL_PREFIX, IP, MAC, PARENT_NETWORK_AR_ID, SIZE, TYPE, ULA_PREFIX, VN_MAD,  **kwargs_)
supermod.ARType.subclass = ARTypeSub
# end class ARTypeSub


class LOCKType118Sub(TemplatedType, supermod.LOCKType118):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType118Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType118.subclass = LOCKType118Sub
# end class LOCKType118Sub


class PERMISSIONSType119Sub(TemplatedType, supermod.PERMISSIONSType119):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType119Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType119.subclass = PERMISSIONSType119Sub
# end class PERMISSIONSType119Sub


class CLUSTERSType120Sub(TemplatedType, supermod.CLUSTERSType120):
    def __init__(self, ID=None, **kwargs_):
        super(CLUSTERSType120Sub, self).__init__(ID,  **kwargs_)
supermod.CLUSTERSType120.subclass = CLUSTERSType120Sub
# end class CLUSTERSType120Sub


class VROUTERSType121Sub(TemplatedType, supermod.VROUTERSType121):
    def __init__(self, ID=None, **kwargs_):
        super(VROUTERSType121Sub, self).__init__(ID,  **kwargs_)
supermod.VROUTERSType121.subclass = VROUTERSType121Sub
# end class VROUTERSType121Sub


class UPDATED_VMSType122Sub(TemplatedType, supermod.UPDATED_VMSType122):
    def __init__(self, ID=None, **kwargs_):
        super(UPDATED_VMSType122Sub, self).__init__(ID,  **kwargs_)
supermod.UPDATED_VMSType122.subclass = UPDATED_VMSType122Sub
# end class UPDATED_VMSType122Sub


class OUTDATED_VMSType123Sub(TemplatedType, supermod.OUTDATED_VMSType123):
    def __init__(self, ID=None, **kwargs_):
        super(OUTDATED_VMSType123Sub, self).__init__(ID,  **kwargs_)
supermod.OUTDATED_VMSType123.subclass = OUTDATED_VMSType123Sub
# end class OUTDATED_VMSType123Sub


class UPDATING_VMSType124Sub(TemplatedType, supermod.UPDATING_VMSType124):
    def __init__(self, ID=None, **kwargs_):
        super(UPDATING_VMSType124Sub, self).__init__(ID,  **kwargs_)
supermod.UPDATING_VMSType124.subclass = UPDATING_VMSType124Sub
# end class UPDATING_VMSType124Sub


class ERROR_VMSType125Sub(TemplatedType, supermod.ERROR_VMSType125):
    def __init__(self, ID=None, **kwargs_):
        super(ERROR_VMSType125Sub, self).__init__(ID,  **kwargs_)
supermod.ERROR_VMSType125.subclass = ERROR_VMSType125Sub
# end class ERROR_VMSType125Sub


class TEMPLATEType126Sub(TemplatedType, supermod.TEMPLATEType126):
    def __init__(self, DNS=None, GATEWAY=None, GATEWAY6=None, GUEST_MTU=None, IP6_METHOD=None, IP6_METRIC=None, METHOD=None, METRIC=None, NETWORK_ADDRESS=None, NETWORK_MASK=None, SEARCH_DOMAIN=None, VCENTER_FROM_WILD=None, VCENTER_INSTANCE_ID=None, VCENTER_NET_REF=None, VCENTER_PORTGROUP_TYPE=None, VCENTER_TEMPLATE_REF=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType126Sub, self).__init__(DNS, GATEWAY, GATEWAY6, GUEST_MTU, IP6_METHOD, IP6_METRIC, METHOD, METRIC, NETWORK_ADDRESS, NETWORK_MASK, SEARCH_DOMAIN, VCENTER_FROM_WILD, VCENTER_INSTANCE_ID, VCENTER_NET_REF, VCENTER_PORTGROUP_TYPE, VCENTER_TEMPLATE_REF, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType126.subclass = TEMPLATEType126Sub
# end class TEMPLATEType126Sub


class AR_POOLType127Sub(TemplatedType, supermod.AR_POOLType127):
    def __init__(self, AR=None, **kwargs_):
        super(AR_POOLType127Sub, self).__init__(AR,  **kwargs_)
supermod.AR_POOLType127.subclass = AR_POOLType127Sub
# end class AR_POOLType127Sub


class ARType128Sub(TemplatedType, supermod.ARType128):
    def __init__(self, AR_ID=None, GLOBAL_PREFIX=None, IP=None, MAC=None, PARENT_NETWORK_AR_ID=None, SIZE=None, TYPE=None, ULA_PREFIX=None, VN_MAD=None, MAC_END=None, IP_END=None, IP6_ULA=None, IP6_ULA_END=None, IP6_GLOBAL=None, IP6_GLOBAL_END=None, IP6=None, IP6_END=None, PORT_START=None, PORT_SIZE=None, USED_LEASES=None, LEASES=None, **kwargs_):
        super(ARType128Sub, self).__init__(AR_ID, GLOBAL_PREFIX, IP, MAC, PARENT_NETWORK_AR_ID, SIZE, TYPE, ULA_PREFIX, VN_MAD, MAC_END, IP_END, IP6_ULA, IP6_ULA_END, IP6_GLOBAL, IP6_GLOBAL_END, IP6, IP6_END, PORT_START, PORT_SIZE, USED_LEASES, LEASES,  **kwargs_)
supermod.ARType128.subclass = ARType128Sub
# end class ARType128Sub


class LEASESTypeSub(TemplatedType, supermod.LEASESType):
    def __init__(self, LEASE=None, **kwargs_):
        super(LEASESTypeSub, self).__init__(LEASE,  **kwargs_)
supermod.LEASESType.subclass = LEASESTypeSub
# end class LEASESTypeSub


class LEASETypeSub(TemplatedType, supermod.LEASEType):
    def __init__(self, IP=None, IP6=None, IP6_GLOBAL=None, IP6_LINK=None, IP6_ULA=None, MAC=None, VM=None, VNET=None, VROUTER=None, **kwargs_):
        super(LEASETypeSub, self).__init__(IP, IP6, IP6_GLOBAL, IP6_LINK, IP6_ULA, MAC, VM, VNET, VROUTER,  **kwargs_)
supermod.LEASEType.subclass = LEASETypeSub
# end class LEASETypeSub


class LOCKType129Sub(TemplatedType, supermod.LOCKType129):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType129Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType129.subclass = LOCKType129Sub
# end class LOCKType129Sub


class PERMISSIONSType130Sub(TemplatedType, supermod.PERMISSIONSType130):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType130Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType130.subclass = PERMISSIONSType130Sub
# end class PERMISSIONSType130Sub


class TEMPLATEType131Sub(TemplatedType, supermod.TEMPLATEType131):
    def __init__(self, VN_MAD=None, anytypeobjs_=None, **kwargs_):
        super(TEMPLATEType131Sub, self).__init__(VN_MAD, anytypeobjs_,  **kwargs_)
supermod.TEMPLATEType131.subclass = TEMPLATEType131Sub
# end class TEMPLATEType131Sub


class PERMISSIONSType132Sub(TemplatedType, supermod.PERMISSIONSType132):
    def __init__(self, OWNER_U=None, OWNER_M=None, OWNER_A=None, GROUP_U=None, GROUP_M=None, GROUP_A=None, OTHER_U=None, OTHER_M=None, OTHER_A=None, **kwargs_):
        super(PERMISSIONSType132Sub, self).__init__(OWNER_U, OWNER_M, OWNER_A, GROUP_U, GROUP_M, GROUP_A, OTHER_U, OTHER_M, OTHER_A,  **kwargs_)
supermod.PERMISSIONSType132.subclass = PERMISSIONSType132Sub
# end class PERMISSIONSType132Sub


class LOCKType133Sub(TemplatedType, supermod.LOCKType133):
    def __init__(self, LOCKED=None, OWNER=None, TIME=None, REQ_ID=None, **kwargs_):
        super(LOCKType133Sub, self).__init__(LOCKED, OWNER, TIME, REQ_ID,  **kwargs_)
supermod.LOCKType133.subclass = LOCKType133Sub
# end class LOCKType133Sub


class VMSType134Sub(TemplatedType, supermod.VMSType134):
    def __init__(self, ID=None, **kwargs_):
        super(VMSType134Sub, self).__init__(ID,  **kwargs_)
supermod.VMSType134.subclass = VMSType134Sub
# end class VMSType134Sub


class ZONETypeSub(TemplatedType, supermod.ZONEType):
    def __init__(self, ID=None, NAME=None, STATE=None, TEMPLATE=None, SERVER_POOL=None, **kwargs_):
        super(ZONETypeSub, self).__init__(ID, NAME, STATE, TEMPLATE, SERVER_POOL,  **kwargs_)
supermod.ZONEType.subclass = ZONETypeSub
# end class ZONETypeSub


class TEMPLATEType135Sub(TemplatedType, supermod.TEMPLATEType135):
    def __init__(self, ENDPOINT=None, **kwargs_):
        super(TEMPLATEType135Sub, self).__init__(ENDPOINT,  **kwargs_)
supermod.TEMPLATEType135.subclass = TEMPLATEType135Sub
# end class TEMPLATEType135Sub


class SERVER_POOLTypeSub(TemplatedType, supermod.SERVER_POOLType):
    def __init__(self, SERVER=None, **kwargs_):
        super(SERVER_POOLTypeSub, self).__init__(SERVER,  **kwargs_)
supermod.SERVER_POOLType.subclass = SERVER_POOLTypeSub
# end class SERVER_POOLTypeSub


class SERVERTypeSub(TemplatedType, supermod.SERVERType):
    def __init__(self, ENDPOINT=None, ID=None, NAME=None, **kwargs_):
        super(SERVERTypeSub, self).__init__(ENDPOINT, ID, NAME,  **kwargs_)
supermod.SERVERType.subclass = SERVERTypeSub
# end class SERVERTypeSub


class TEMPLATEType136Sub(TemplatedType, supermod.TEMPLATEType136):
    def __init__(self, ENDPOINT=None, **kwargs_):
        super(TEMPLATEType136Sub, self).__init__(ENDPOINT,  **kwargs_)
supermod.TEMPLATEType136.subclass = TEMPLATEType136Sub
# end class TEMPLATEType136Sub


class SERVER_POOLType137Sub(TemplatedType, supermod.SERVER_POOLType137):
    def __init__(self, SERVER=None, **kwargs_):
        super(SERVER_POOLType137Sub, self).__init__(SERVER,  **kwargs_)
supermod.SERVER_POOLType137.subclass = SERVER_POOLType137Sub
# end class SERVER_POOLType137Sub


class SERVERType138Sub(TemplatedType, supermod.SERVERType138):
    def __init__(self, ENDPOINT=None, ID=None, NAME=None, STATE=None, TERM=None, VOTEDFOR=None, COMMIT=None, LOG_INDEX=None, FEDLOG_INDEX=None, **kwargs_):
        super(SERVERType138Sub, self).__init__(ENDPOINT, ID, NAME, STATE, TERM, VOTEDFOR, COMMIT, LOG_INDEX, FEDLOG_INDEX,  **kwargs_)
supermod.SERVERType138.subclass = SERVERType138Sub
# end class SERVERType138Sub


def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    rootClass = supermod.GDSClassesMapping.get(tag)
    if rootClass is None and hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
##     if not silence:
##         sys.stdout.write('<?xml version="1.0" ?>\n')
##         rootObj.export(
##             sys.stdout, 0, name_=rootTag,
##             namespacedef_='',
##             pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    mapping = {}
    rootElement = rootObj.to_etree(None, name_=rootTag, mapping_=mapping)
    reverse_mapping = rootObj.gds_reverse_node_mapping(mapping)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
##     if not silence:
##         content = etree_.tostring(
##             rootElement, pretty_print=True,
##             xml_declaration=True, encoding="utf-8")
##         sys.stdout.write(content)
##         sys.stdout.write('\n')
    return rootObj, rootElement, mapping, reverse_mapping


def parseString(inString, silence=False):
    if sys.version_info.major == 2:
        from StringIO import StringIO
    else:
        from io import BytesIO as StringIO
    parser = None
    rootNode= parsexmlstring_(inString, parser)
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        rootNode = None
##     if not silence:
##         sys.stdout.write('<?xml version="1.0" ?>\n')
##         rootObj.export(
##             sys.stdout, 0, name_=rootTag,
##             namespacedef_='')
    return rootObj


def parseLiteral(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'HISTORY_RECORDS'
        rootClass = supermod.HISTORY_RECORDS
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
##     if not silence:
##         sys.stdout.write('#from supbind import *\n\n')
##         sys.stdout.write('from . import supbind as model_\n\n')
##         sys.stdout.write('rootObj = model_.rootClass(\n')
##         rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
##         sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()
