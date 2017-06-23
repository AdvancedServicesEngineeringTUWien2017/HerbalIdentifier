# README
This project contains a mini project for Advanced Services Engineering at the Technical University of Vienna and should provide an image classification service as well as a manual classification service and retraining the network via a Hadoop Spark computing engine.

# basic description

Be aware that every node needs to have at least 8GB of RAM

The classify folder is meant to be dployed on the classify service node(s) which could be aggregated via a load balancer.
The sparkmaster folder is meant to be deployed on the SPARK masters node


# deploy
## Spark Master

Install Docker on the node

Copy the FILES of the sparkmaster folder to root/ of the appropriate node.

	cd ~/tensorflow-spark-docker

copy jdk 8u121 as tar file into the jdk folder

Now build the image:
	
	./buildimage.sh

Fill the folders with sample images (each folder generates a new label):
	
	cd ~/pythonservice/tf_files/flower_photos

You need aprox. 400 images to get a good result in training

Start the Docker image:

	cd ~
	./startdocker.sh

## Classify Service Deploy

Copy the classify folder into the root/ directory

Build and Start the Docker image:

	cd ~/classify
	./buildimage.sh
	./startdocker.sh

If your SparkMaster server is already running and all the scp commands in the app.py are configured, run http://yourdomain.sparkmaster.com/retrain to get the initial training and if the accuracy is above 90%, the nodes should be synced.


## Known Bugs

- Prone to SQL injection
- No SSL encryption
- Not finished
- just a Prototype

The Project uses [Tensorflow] and [tensoronspark].

[Tensorflow]: https://github.com/tensorflow/tensorflow/tree/master/tensorflow/tools/docker
[tensoronspark]: https://github.com/liangfengsid/tensoronspark
