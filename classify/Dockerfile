	#FROM gcr.io/tensorflow/tensorflow:latest
	FROM tensorflow/tensorflow:1.2.0 
	EXPOSE 80
	RUN apt-get update
	RUN apt-get install -y vim
	RUN pip install flask requests
	
	RUN mkdir /root/pythonservice	
	ENTRYPOINT python /root/pythonservice/app.py
