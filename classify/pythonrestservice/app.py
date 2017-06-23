#!flask/bin/python
import os
import requests
import tensorflow as tf, sys
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/root/pythonservice/uploads'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
	    image_path = os.path.join(UPLOAD_FOLDER,filename)

	    # Read in the image_data
	    image_data = tf.gfile.FastGFile(image_path, 'rb').read()

	    # Loads label file, strips off carriage return
	    label_lines = [line.rstrip() for line
                   in tf.gfile.GFile("/root/pythonservice/tf_files/retrained_labels.txt")]

	    # Unpersists graph from file
	    with tf.gfile.FastGFile("/root/pythonservice/tf_files/retrained_graph.pb", 'rb') as f:
    	      graph_def = tf.GraphDef()
    	      graph_def.ParseFromString(f.read())
    	      _ = tf.import_graph_def(graph_def, name='')

	    with tf.Session() as sess:
    	     # Feed the image_data as input to the graph and get first prediction
    	     softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

    	    predictions = sess.run(softmax_tensor, \
               {'DecodeJpeg/contents:0': image_data})

    	    # Sort to show labels of first prediction in order of confidence
    	    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
	    scores = ''
	    highestscore = 0.0
	    label = ''
	    result = ''
   	    for node_id in top_k:
        	human_string = label_lines[node_id]
        	score = predictions[0][node_id]
        	print('%s (certainty = %.5f)' % (human_string, score))
		if score>highestscore :
			highestscore=score
			label=human_string
		#scores = scores + ('%s (certainty = %.5f)' % (human_string, score))+'<br>'
    	    if highestscore>0.85 :
		result = result + 'I am quite sure that this is a '+label
	    if highestscore>0.75 and highestscore<0.85 :
		result = result + 'I am not so sure, but it might be a '+label
	    if highestscore<0.75 :
		url = 'http://sparkmaster.yourdomain.com/unclassifiedimage'
                files = {'file': open(os.path.join(UPLOAD_FOLDER, filename), 'rb')}
		try:
			r = requests.post(url, files=files)
		except :
			pass
		# Maybe set up for a retry, or continue in a retry loop
		#except requests.exceptions.TooManyRedirects:
    		# Tell the user their URL was bad and try a different one
		#except requests.exceptions.RequestException as e:
    		# catastrophic error. bail.
   
		result = result + 'I am sorry, I cant identify your image'	
	    return '''
    			<!doctype html>
    			<head>
			<title>Herbal Identifier</title>
    			<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
			</head>
			<body>
			<h1>'''+ filename +': '+result +'''</h1>
    			<form method=post enctype=multipart/form-data>
      			<p><input type=file name=file>
         			<input type=submit value=Upload>
    			</form>
			'''+scores+'''</body>'''
	   # return redirect(url_for('upload_file'+scores,
           #                         filename=filename))
    return '''
     <!doctype html>
                        <head>
                        <title>Herbal Identifier</title>
                        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
                        </head>
                        <body>
                        <h1>Upload new File</h1>
                        <form method=post enctype=multipart/form-data>
                        <p><input type=file name=file>
                                <input type=submit value=Upload>
                        </form>'''
		

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)

