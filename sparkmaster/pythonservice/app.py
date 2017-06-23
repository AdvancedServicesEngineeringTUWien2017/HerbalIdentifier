#!flask/bin/python
import os,random,MySQLdb,time,os.path
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/root/pythonservice/static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)

if os.path.exists("/db.lock") == False :
	time.sleep(15)
db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="dbuser",         # your username
                     passwd="dbpass",  # your password
                     db="classifydb")        # name of the data base

cur = db.cursor()

if os.path.exists("/db.lock") == False :
	cur.execute("CREATE TABLE IF NOT EXISTS imagescores ( id int NOT NULL AUTO_INCREMENT,imagename varchar(255),imagelabel varchar(255),imagescore int, PRIMARY KEY (id))")
	cur.execute("CREATE TABLE IF NOT EXISTS labelnames ( id int NOT NULL AUTO_INCREMENT,labelname varchar(255), PRIMARY KEY (id))")
	file = open('/db.lock', 'w+')



with open("/root/pythonservice/tf_files/retrained_labels.txt") as f:
    content = f.readlines()
    content = [x.strip() for x in content] 

for line in content:
	cur.execute('SELECT 1 FROM labelnames WHERE labelname="'+line+'"')
	if not cur.fetchone():
		cur.execute('INSERT INTO labelnames (labelname) VALUES ("'+line+'")')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/unclassifiedimage', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print "no file part"
	    flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
	    print "no filename"
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
	    print "file passt"
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
	    cur.execute('SELECT 1 FROM imagescores WHERE imagename="'+filename+'"')
            if not cur.fetchone():
                cur.execute('INSERT INTO imagescores (imagename) VALUES ("'+filename+'")')
            return redirect(url_for('upload_file',
                                    filename=filename))
    options='<select><option value="dontknow">Dont know</option>'
    cur.execute("SELECT labelname FROM labelnames")
    for row in cur.fetchall():
	options=options+'<option value="'+row[0]+'">'+row[0]+'</option>'	
    options=options+'</select>'
    return '''
    <!doctype html>
    <title>Manual Image Classifier</title>
    <h1>Please classify following image</h1>
<img src="/static/'''+ random.choice(os.listdir("/root/pythonservice/static")) +'''">
'''+options+'''    
<form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
@app.route('/classify', methods=['GET'])
def classify():
    if 'filename' in request.args and 'label' in request.args:
	print "argumente vorhanden ... !!!!!"
	if request.args.get('newlabel')!='':
		        cur.execute('SELECT 1 FROM labelnames WHERE labelname="'+request.args.get('newlabel')+'"')
        		if not cur.fetchone():
                		cur.execute('INSERT INTO labelnames (labelname) VALUES ("'+request.args.get('newlabel')+'")')
        cur.execute('SELECT 1 FROM imagescores WHERE imagename="'+request.args.get('filename')+'"')
        if not cur.fetchone():
                cur.execute('INSERT INTO imagescores (imagename) VALUES ("'+request.args.get('filename')+'")')
	cur.execute('SELECT * FROM imagescores WHERE imagename="'+request.args.get('filename')+'"')
        row = cur.fetchone()
	print row
	if row[3]==None and request.args.get("label")!="dontknow":
		cur.execute('UPDATE imagescores SET imagescore=30,imagelabel="'+request.args.get("label")+'" WHERE imagename="'+request.args.get("filename")+'"')
	if row[3]!=None and request.args.get("label")!="dontknow":
		newscore = row[3]
		if row[2]==request.args.get("label") :
			newscore=newscore+30
		if row[2]!=request.args.get("label") :
			newscore=newscore-60
		cur.execute('UPDATE imagescores SET imagescore='+str(newscore)+',imagelabel="'+request.args.get("label")+'" WHERE imagename="'+request.args.get("filename")+'"')





    options='<select name="label"><option value="dontknow">Dont know</option>'
    cur.execute("SELECT labelname FROM labelnames")
    for row in cur.fetchall():
        options=options+'<option value="'+row[0]+'">'+row[0]+'</option>'
    options=options+'</select>'
    imagename=random.choice(os.listdir("/root/pythonservice/static"))
    return '''
    <!doctype html>
    <title>Manual Image Classifier</title>
    <h1>Please classify following image</h1>
<img src="/static/'''+ imagename +'''">
<form action="/classify" method="get">
'''+options+'''   
<input type="hidden" name="filename" value="'''+imagename+'''"> 
<input type="text" name="newlabel"><br>  
<input type="submit" value="Submit">    
</form>
    '''


@app.route('/retrain', methods=['GET'])
def retrain():
	os.system('cd /root/pythonservice && ./train.sh &')
	return ''

@app.route('/sync', methods=['GET'])
def sync():
        os.system('sshpass -p "passwd" scp /root/pythonservice/tf_files/retrained_graph.pb root@classify1.yourdomain.com:/root/classify/pythonrestservice/tf_files/retrained_graph.pb')
        os.system('sshpass -p "passwd" scp /root/pythonservice/tf_files/retrained_labels.txt root@classify1.yourdomain.com:/root/classify/pythonrestservice/tf_files/retrained_labels.txt')
        os.system('sshpass -p "passwd" scp -r /root/pythonservice/tf_files/inception root@classify1.yourdomain.com:/root/classify/pythonrestservice/tf_files/inception') 
	os.system('sshpass -p "passwd" scp /root/pythonservice/tf_files/retrained_graph.pb root@classify2.yourdomain.com:/root/classify/pythonrestservice/tf_files/retrained_graph.pb')
        os.system('sshpass -p "passwd" scp /root/pythonservice/tf_files/retrained_labels.txt root@classify2.yourdomain.com:/root/classify/pythonrestservice/tf_files/retrained_labels.txt')
        os.system('sshpass -p "passwd" scp -r /root/pythonservice/tf_files/inception root@classify2.yourdomain.com:/root/classify/pythonrestservice/tf_files/inception') 
	return ''

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
