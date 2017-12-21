# Magic Lanterns
Raspberry Pi powered lanterns that synchronize over the Internet. Press a button on one and they all light up. Press the button again on any one and they change to the next pattern. A long press turns them off.

[![IMAGE ALT TEXT](https://i.imgur.com/A1nfFZ1.png)](http://www.youtube.com/watch?v=UhniE0tFbiw "Video Title")


## Technologies Used
* Raspberry Pi
* Python
* Amazon Web Services
* Ansible

## Parts List
* Raspberry Pi Zero W, power supply, and an SD card
* [2x20 pin GPIO header](https://www.adafruit.com/product/2822)
* [Pimoroni Unicorn pHAT](https://shop.pimoroni.com/products/unicorn-phat)
* Push buttons, for example: [http://a.co/hGVCNbj](http://a.co/hGVCNbj)
* Lanterns with white frosted glass
* Velcro w/ sticky tape

## Assembly
After soldering the GPIO header to the RPi and soldering the female GPIO header that comes with the Unicorn pHAT, the Unicorn pHAT will connect right to the RPi. 

Wire a push button to pins 6 (ground) and 11 (BCM17). 

Stick the RPi to the inside of the lantern using the velcro w/ sticky tape (or possibly using some more advanced mounting method if you are so inclined). 

## Installation

I have included an Ansible playbook that creates the AWS environment for you (an IAM user, SNS Topic, and SQS Queues). The playbook can be run from any system. I'd recommend against running it on one of the RPi's that will be going in your lantern, because it requires credentials that have the ability to create the AWS configuration. We'll want our lanterns to only have permissions to post to SNS and pull from the SQS queues. The playbook is written for two lanterns, but if you wish to have more lanterns in a given group just modify playbook and answerfile accordingly.  

First, use the [AWS cli](https://aws.amazon.com/cli/) to create the profile that will be used by the Ansible playbook.

`aws configure --profile "magic-lanterns"` 

Provide the Access Key ID and the Secret Access Key of a user that has the rights to create the configuration noted above. It will also prompt you for the AWS region you wish to use (e.g. "us-east-1"). Then edit `answerfile.yml` and specify the region and the AWS account ID. 

[Install Ansible](http://docs.ansible.com/ansible/latest/intro_installation.html) if you don't already have it, then do the following to install the dependencies and run the playbook (from the `ansible` directory of the repo):

    pip install boto
    ansible-playbook aws.yml

Take note of the SNS Topic and SQS Queue URLs that it outputs. 

Next, perform the remaining steps on each RPi (tested on Rasbian Stretch Lite).

Note we are going to run everything as root, because the code requires access to the GPIO pins.

    su - root

Install the necessary dependencies:

    apt-get install npm python3-rpi.gpio python3-pip git ntp
    pip3 install awscli unicornhat
    ln -s /usr/bin/nodejs /usr/bin/node
    npm install pm2@latest -g

Populate the AWS credentials of the lantern user that was created by the Ansible playbook. Log into the AWS console, and generate credentials from IAM for the "lantern-user". Then run:

    aws configure --profile "magic-lanterns"
    
Provide the Access Key ID and the Secret Access Key that you retrieved from the AWS console, and provide the region. 

If you haven't already, clone the repo or otherwise copy the code to your RPi. Edit the following items in `lantern.config.js`:

* SNS\_TOPIC: The SNS\_TOPIC that was output when you ran the Ansible playbook
* PROFILE: The profile name you specified when you ran the `aws configure` command on your RPi. Be sure to update both lines that reference PROFILE.
* SQS\_QUEUE\_URL: The SQS\_QUEUE\_URL that the Ansible playbook output for this lantern. The playbook will create one SQS\_QUEUE\_URL for each lantern. Use the first one on your first lantern, the second one on you second lantern, etc. 

Now you are ready to install the code requirements, and to use [PM2](https://github.com/Unitech/pm2) to start the lantern code and to ensure that the it starts on boot.

    pip3 install -r requirements.txt 
    pm2 start lantern.config.js
    pm2 startup
    pm2 install pm2-logrotate
    
To turn off the RPi status LEDs on an RPi Zero, add the add the following lines to `/boot/config.txt` and reboot:

    dtparam=act_led_trigger=none
    dtparam=act_led_activelow=on

I'd strongly recommend implementing [read-only mode for Rasbian](https://learn.adafruit.com/read-only-raspberry-pi/overview) to protect against SD card corruption. If you do so, do the following to create an OverlayFS mount point to allow PM2 to write its logs and whatnot:

    echo overlay >> /etc/modules

And add the following to `/etc/rc.local`:

    mkdir /tmp/pm2 /tmp/pm2-work 
    mount -t overlay overlay -olowerdir=/root/.pm2,upperdir=/tmp/pm2,workdir=/tmp/pm2-work /root/.pm2 

Then apply the read-only mode configuration as per the Adafruit documentation.


## AWS Costs
TL;DR: it will probably be free. 

Pushing the button posts a notification to SNS. The first 1 million SNS requests per month are free. So it is safe to say that you are unlikely to incur any charges there. 

The SNS Topic fans out a message to each SQS Queue. There is no charge for deliveries to SQS Queues. 

Lastly, each lantern polls it's queue for messages. We are using [long polling](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html), and therefore each lantern will make up to 86,000/20*31=133,920 calls per month. The first 1 million SQS queries per month are free, so unless you have more than 7 lanterns on a given account your costs will be zero. If you do add an 8th lantern your costs will balloon to 40 cents / month USD (up to 14 lanterns), because after your first free 1 million requests AWS charges $0.40 USD / million requests. 

## Have Fun!
Hope you have fun building this project, and let me know if you spot any problems. 