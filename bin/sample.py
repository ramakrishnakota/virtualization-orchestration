from bottle import route, run,get, post, request
import bottle
import socket
import fcntl
import struct
from xml.dom.minidom import parseString
import xml.etree.cElementTree as ET
import sys
import socket
import libvirt
import os
from collections import defaultdict
counter=3800
pmv_mapping=defaultdict(list)
vmid_mapping=dict()
vmtype_mapping=dict()
images=dict()
impaths=dict()
pms=dict()
instance_types=dict()
str3=dict()
str2=dict(dict())
pmcon_mapp=dict()
fullpath=dict()
hostname=None
def main():
    path=sys.argv[1]
    f=open(path,'r')
    id1=100
    for line in f:
        global images
        global impaths
        global fullpath
        global hostname
        fullpath.update({id1 : line.rstrip()})
        str4=line.split(':')[-1]
        str1=line.split('/')[-1]
        impaths.update({id1 : str4.rstrip()})
        images.update({id1 : str1.rstrip()})
        id1+=1
    f.close()
    path=sys.argv[2]
    f=open(path,'r')
    id1=1
    for line in f:
        global pms
        str4=line.split('/')[-1]
        pms.update({id1 : str4.rstrip()})
        conn=libvirt.open("remote+ssh://"+str4.rstrip()+"/system")
        pmcon_mapp.update({id1 : conn})
        id1+=1
    f.close()
    global instance_types
    global str2
    global str3
    str3=1,2,3
        
    instance_types={1 : 512,2 : 1024,4 : 2048}
    
    str2[str3[0]]={1:512}
    str2[str3[1]]={2:1024}
    str2[str3[2]]={4:2048}
    
    for k in pms.values():
        
    
        for v in fullpath.values():
            os.system('scp -B '+v+' '+k+':/home')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname=socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s', 'eth0'[:15]))[20:24])
           
            
 
@route('/pm/<pmid>')
def pm_query(pmid):
    global pms
    pmid=int(pmid)
    conn=pmcon_mapp.get(pmid)
    type1=conn.getType()
    numcpus=conn.getMaxVcpus(type1)
    freemem=conn.getFreeMemory()/(1024.0*1024.0*1024)*8
    host=pms.get(pmid)
    totaldisk=os.popen('ssh '+host+' df -h | grep "^/dev/[hs]d" | awk "{s+=\$2} END {print s}"').read()
    freedisk=os.popen('ssh '+host+' df -h | grep "^/dev/[hs]d" | awk "{s+=\$4} END {print s}"').read()
    totaldisk=totaldisk.rstrip()+"GB"
    freedisk=freedisk.rstrip()+"GB"
    nodeinfo=conn.getInfo()
    s=nodeinfo.pop(2)
    acpus=int(s)
    cpu=0
    domains=0
    for id in conn.listDomainsID():
        domains+=1
        dom = conn.lookupByID(id)
        info=dom.info()
        s=info.pop(3)
        cpu+=int(s)
    freecpus=numcpus-cpu
    s=nodeinfo.pop(1)
    totalmem=(float(s)/1024.0)
    out=[{'pmid':pmid,'capacity':{'cpu':numcpus,'ram':totalmem,'disk':totaldisk},'free':{'cpu':freecpus,'ram':freemem,'disk':freedisk},'vms':domains}]
    return {'pmid':out}
         
@route('/vm/query')
def vm_query():
    x=request.query.get('vmid')
    x=int(x)
    conn=libvirt.open("qemu:///system")
    for key,values in vmid_mapping.iteritems():
        if key==x:
            id1=values
            break
    
    dom=conn.lookupByID(id1)
    for key,values in vmtype_mapping.iteritems():
        if key==x:
            in_type=values
            break
    for key,values in pmv_mapping.iteritems():
        for i in values:
            if i==x:
                pmid=key
                break
        break
            
            
      
        
            

    out=[{'vmid':x,'name':dom.name(),'vm_type':in_type,'pmid':pmid}]
    return {"vm-details":out}

@route('/vm/destroy')
def vm_destroy():
    vmid=request.query.get('vmid')
    global pmv_mapping
    global vmid_mapping
    vmid=int(vmid)
    for key,values in pmv_mapping.iteritems():
        for i in values:
            if i==vmid:
                pmid=key
                values.remove(vmid)
                break
        break
        
            
    conn=pmcon_mapp.get(pmid)
    for key,values in vmid_mapping.iteritems():
        if key==vmid:
            x=values
            del vmid_mapping[key]
            break
    dom=conn.lookupByID(x)
    check=dom.destroy()
    if(check==0):
        return {"status": 1}
    else:
        return {"status": 0}

       

@route('/image/list')
def list_images():
       
    out = [{'id': key, 'name':images[key]} for key in images.keys()]
    return {'images':out}
    
@route('/pm/list')
def list_pms():
    
    out=[{'pmid':key} for key in pms.keys()]
    return {'pmids':out}
 
@route('/vm/types')
def list_types():
    global str2
    
        
    out=[{'tid':i,'cpu':k ,'ram':l } for i,j in str2.iteritems() for k,l in j.iteritems()]
    return {'types':out}
@route('/pm/<pmid>/listvms')
def list_vms(pmid):
    global pmv_mapping
    pmid=int(pmid)
    out=[{'vmids':values} for key,values in pmv_mapping.iteritems()]
    return {'vmids':out}
    

    
        
@route('/vm/create')
def vm_create():
    name =request.query.get('name')
    vm_type=request.query.get('vm_type')
    image_type=request.query.get('image_type')
    global counter
    global pmv_mapping
    global vmid_mapping
    global vmtype_mapping
    global pmcon_mapp
    vm_type=int(vm_type)
    image_type=int(image_type)
    memory1=int(instance_types.values()[vm_type-1])*1000
    vcpu1=instance_types.keys()[vm_type-1]
    machine_id=scheduler(memory1,vcpu1)
    conn=pmcon_mapp.get(machine_id)
                
   
    xml=conn.getCapabilities()
    image_path="/var/lib/libvirt/images/"
    image_name=images.get(image_type)
    
    name1=name
    type1=conn.getType()
    if (type1=="xen"):
        dev1='xvdd'
        bus='xen'
        dname='tap'
        dtype='qcow'
    else:
        dev1="hda"
        bus='ide'
        dname='qemu'
        dtype='raw'
    dom = parseString(xml)
    arch = dom.getElementsByTagName('arch')[0].firstChild.data
    emulator=dom.getElementsByTagName('emulator')[0].firstChild.data
    os_type= dom.getElementsByTagName('os_type')[0].firstChild.data
    machine=dom.getElementsByTagName('machine')[0].firstChild.data
    vm_createxml(name1,memory1,vcpu1,image_name,type1,arch,emulator,os_type,image_path,dev1,bus,dname,dtype,machine)
    filename="vm.xml"
    f=open(filename,'r')
    xmlconfig=f.read()

    dom=conn.createXML(xmlconfig,0)
    id=dom.ID()
    pmv_mapping[machine_id].append(counter)
    vmid_mapping.update({counter:id})
    vmtype_mapping.update({counter:vm_type})
    counter+=1
    return {"vmid" : (counter-1)}

def vm_createxml(name1,memory1,vcpu1,image_name,type1,arch,emulator,os_type,image_path,dev1,bus,dname,dtype,machine):
    
    
    memory1=str(memory1)
    vcpu1=str(vcpu1)
    type1=str(type1)
    type1=type1.lower()

    
    domain = ET.Element("domain")
    domain.set("type",type1)

    name = ET.SubElement(domain, "name")
    name.text=name1
    memory = ET.SubElement(domain, "memory")
    memory.text=memory1
    vcpu = ET.SubElement(domain, "vcpu")
    vcpu.text=vcpu1
    if (type1=='xen'):
        bootloader=ET.SubElement(domain, "bootloader")
        bootloader.text='/usr/bin/pygrub'
    os = ET.SubElement(domain, "os")
    type1=ET.SubElement(os, "type")
    type1.set("arch",arch)
    type1.set("machine",machine)
    type1.text=os_type
    if (type1=='qemu'):
        boot=ET.SubElement(os, "boot")
        boot.set("dev","hd")
        
    features = ET.SubElement(domain, "features")
    acpi = ET.SubElement(features, "acpi")
    apic = ET.SubElement(features, "apic")
    pae = ET.SubElement(features, "pae")
    on_poweroff = ET.SubElement(domain, "on_poweroff")
    on_poweroff.text="destroy"
    on_reboot = ET.SubElement(domain, "on_reboot")
    on_reboot.text="restart"
    on_crash = ET.SubElement(domain, "on_crash")
    on_crash.text="restart"
    devices = ET.SubElement(domain, "devices")
    emulator = ET.SubElement(devices, "emulator")
    emulator.text=emulator
    disk = ET.SubElement(devices, "disk")
    disk.set("type","file")
    disk.set("device","disk")
    driver = ET.SubElement(disk, "driver")
    driver.set("name",dname)
    driver.set("type",dtype)
    source = ET.SubElement(disk, "source")
    source.set("file",image_path+image_name)
    target = ET.SubElement(disk, "target")
    target.set("dev",dev1)
    target.set("bus",bus)
    address = ET.SubElement(disk, "address")
    address.set("type","drive")
    address.set("controller","0")
    address.set("bus","0")
    address.set("unit","0")

    tree = ET.ElementTree(domain)
    tree.write("vm.xml")

def scheduler(memory1,vcpu1):
    memory1=(memory1/1000)/1024.0
    pm_mem=dict()
    cpu=0
    global pmcon_mapp
    j=1
    for i,v in pmcon_mapp.iteritems():
        freemem=v.getFreeMemory()/(1024.0*1024.0*1024)*8
        type1=v.getType()
        numcpus=v.getMaxVcpus(type1)
        for id in v.listDomainsID():
            dom = v.lookupByID(id)
            info=dom.info()
            s=info.pop(3)
            cpu+=int(s)
        freecpus=numcpus-cpu
        if (freemem>=memory1 and freecpus>=vcpu1):
            hash1=(freemem-memory1)+(freecpus-vcpu1)
            pm_mem.update({j:hash1})
            j+=1
    list_sorted= sorted(pm_mem,key=pm_mem.get)
    return list_sorted[0]
    
         
        
    
   
if __name__ == '__main__':
    main()
run(host=hostname, port=80)
