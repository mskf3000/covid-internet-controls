# Ansible

For configuration management, Ansible is used in order to secure each host and deploy the latest software changes.

## Ansible Command & Control Server

The Ansible command and control server (C&C) is responsible for handling all requests to each given VPS.

Setup for this C&C server is as follows:

1. Install Ansible

  		sudo apt-add-repository ppa:ansible/ansible
		sudo apt install ansible
#sahil modification:
<br> sudo apt update
<br> sudo apt install software-properties-common
<br> sudo apt-add-repository --yes --update ppa:ansible/ansible
<br> sudo apt install ansible

2. Create/modify `/etc/ansible/hosts`, which contains the IP addresses of managed hosts. Note that this file contains addresses with a prefix for easier understanding of which country a VPS resides in, rather than an IP address.

		Korea 			ansible_host=xx.xx.xx.xx
		...

3. Ensure that the following files are present in the `ansible` directory:

	1.  `.env`, which contains the ROOT_PASSWORD.
	2.  `authorized_keys`, which contains the SSH keys for the users that are authorized to SSH into each VPS.
	3.  `cert.pem`, the certificate file for HTTPS communication to each VPS.
	4.  `key.pem`, the key file for HTTPS communication to each VPS.
	5.  `.worker.env`, which contains the REQUEST_KEY for verifying POST requests to each VPS.


## Onboarding a New VPS

To configure a new host to be ready for Ansible management, you must perform the following:

1. Copy over the SSH key for connection:
	
		ssh-copy-id {server IP address}

## Ansible Deployment

To run an ansible playbook, you will need to perform the following:

 1. Switch to the root acccount
	
		sudo -s

2. Enter the `ansible` directory:

		cd ansible/

3. Run a given playbook:

		ansible-playbook deploy.yml


This will execute the playbook against all of the hosts that exist in `/etc/ansible/hosts`.

## Sahil Instructions:
1. changes in ansible.cfg: <become: true, become_method: sudo> 
2. Host file: Rochester_US ansible_host=129.21.183.44 ansible_user=sg5414
3. Command: ansible-playbook deploy.yml -k -K
4. command on slave VPS: apt install python-docker
<br>Packages on query_worker.py host:</br>
5. sudo apt-get install python3-pip
6. sudo pip3 install coloredlogs
7. sudo pip3 install mysql-connector
8. sudo pip3 install python-dotenv
9. For csec rit server: sudo chmod 777 -R .ansible/* . It needs to permission to be modified by remote user as it can't access the .ansible/tmp folder for its operations.
10. New cmd for ansible execution: ansible-playbook deploy.yml
11. Install Ansible instruction (luke one install old version)

<br>  sudo apt update
<br>  sudo apt install software-properties-common
<br>  sudo apt-add-repository --yes --update ppa:ansible/ansible
<br> sudo apt install ansible
12. Usefull crontab command (/etc/crontab)
<br >A. */1 * * * * root /home/sg5414/cronjontestfolder/test1/test.sh
<br >B. 0 9 * * 0 root /home/sg5414/cronjontestfolder/test1/test.sh
(Meaning: At 09:00 on Sunday)
<br>13. Error on VPS host: 
<br>E: Release file for http://dl.google.com/linux/chrome/deb/dists/stable/Release is not valid yet (invalid for another 2h 45min 28s). Updates for this repository will not be applied.
<br>E: Release file for http://us.archive.ubuntu.com/ubuntu/dists/bionic-updates/InRelease is not valid yet (invalid for another 4h 34min 33s). Updates for this repository will not be applied.
<br><b>Solution: sudo hwclock --hctosys (You need to fix the clock in this case, check using date if clock is back in time or not)	
<br>14. Error: Err:7 http://mirrors.digitalocean.com/ubuntu cosmic Release
  404  Not Found [IP: 104.24.117.209 80]
Ign:8 http://archive.ubuntu.com/ubuntu cosmic InRelease

<br>Solution: If you want to continue using an outdated release then edit /etc/apt/sources.list and change archive.ubuntu.com and security.ubuntu.com to old-releases.ubuntu.com.
then update with:

    sudo apt-get update && sudo apt-get dist-upgrade

14. Downgrading from ubuntu 18.10 to 18.04. (To avoid error in 13)
https://linuxconfig.org/how-to-downgrade-ubuntu-linux-system-to-its-previous-version

15. Avoiding error in 13:
https://askubuntu.com/questions/1188970/e-the-repository-http-old-releases-ubuntu-com-ubuntu-bionic-old-releases-rel

16. Install pip3 whereever pip3 is not installed. (VPS + query machine)
Sol: apt install python3-pip

17. Mannual building and running of docker container:
Run the following command in respective order in effected VPS:
<br>1. docker build -t worker /src/worker
<br>2. docker run -p 42075:42075 workers &
<br>3. docker ps (helps to check if docker container is up and running)
<br>

## Sahil: In case 3.6 is installed from source code
A. To set python3.6 as default python3 interpreter
sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.6 2
sudo update-alternatives --config python3

B. Follow these instructions to make pip3 install work: (Link: https://blog.csdn.net/weixin_42730667/article/details/100260883)
1. sudo find / -name 'lsb_release.py'
// result:
// /usr/share/pyshared/lsb_release.py
// /usr/lib/python2.7/dist-packages/lsb_release.py
// /usr/lib/python3/dist-packages/lsb_release.py
2. python -V
3. sudo cp  /usr/lib/python3/dist-packages/lsb_release.py /opt/ptyhon3.7/lib/python3.7

## Sahil ToDo:
1. Make step 4 (python-docker) as part of ansible deploy.yml file.
2. Step 3 needs to be automated via host inventory file.
<br>See these link for reference:
<br>https://stackoverflow.com/questions/37004686/how-to-pass-a-user-password-in-ansible-command
<br>https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html#hosts-and-users
