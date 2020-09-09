# covid-internet-controls

This respository serves as the basis for all content related to the hunt for COVID-19 censorship detection.


## Worker

Each VPS that is used for gathering data is classified as a `worker`.

To learn more, read `worker/README.md`.

## Ansible

For configuration management, Ansible is used in order to secure each host and deploy the latest software changes.

To learn more, read `ansible/README.md`.


## Testing

This project utilizes `pytest` for performing all code testing.

To run these tests, first install `pytest`:

    pip install pytest

Then run the tests:

    pytest

## Sahil: Need to rewrite all the instructions for deployment
1. website_list.txt should contains all the website in given sample format.
2. query_worker_multiple_targets.sh is wrapper script which takes multiple target websites from website_list.txt file.
3. Next ToDo's:
<br>0. update website_list.txt from fakewebsite.links + HB good website + add date field in mysql database in request table.
<br>1. Add random function in worker forloop to send a  website to different workers at random gap of 2 to 4 minutes. + Add same random function in wrapper script in target loop.
<br>2. Now going to make HB1 as my C&C command center.
<br>3. Test wrapper script on HB1.
<br>4. Add VPSes in ansible host config file (workers.py) and test the wrapper script.

### Sahil: Cron job instructions (https://www.ostechnix.com/a-beginners-guide-to-cron-jobs/)
11. Run a job every Sunday:
0 0 * * SUN <command-to-execute>
Or,
0 0 * * 0 <command-to-execute>
It will run at exactly at 00:00 on Sunday.
