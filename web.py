import codecs
import os
import time
from datetime import datetime
from multiprocessing import Process
from uuid import uuid4

from flask import render_template, request, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename, redirect

from app import app
from keyword_cleaner import KeywordCleaner
from util.io import RedisClient
from util.log import get_logger

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'upload')
# These are the extension that we are accepting to be uploaded
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # Accept max 1GB file

logger = get_logger(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/keyword/batch-clean', methods=['POST'])
def keyword_batch_clean():
    job_id = str(uuid4())
    # Get form parameters

    file_text = request.files.get('file_text')

    file_com = os.path.splitext(secure_filename(file_text.filename))
    file_text_name = file_com[0]
    file_text_path = os.path.join(app.config['UPLOAD_FOLDER'], '%s_input-with-job-id_%s%s' %
                                  (file_text_name, job_id, file_com[1]))

    with open(file_text_path, 'w') as f:
        file_text.save(f)

    try:
        with codecs.open(file_text_path, 'r', encoding='utf-8') as f:
	    keywords = f.read().splitlines()

    except UnicodeDecodeError, e:
        logger.exception(e)
        return render_template('message.html', message='ERROR: Your input file "%s" must be in UTF-8 encoding'
                                                       % file_text.filename)
    except Exception, e:
        logger.exception(e)
        return render_template('message.html', message='ERROR: Failed to read file "%s" - %s'
                                                       % (file_text.filename, e.message))

    output_file = '%s_result-for-job_%s.txt' % (file_text_name, job_id)
    process = Process(target=_process_job, args=(job_id, keywords, output_file, app.config['UPLOAD_FOLDER']))
    process.start()

    return redirect(url_for('job_list'))


@app.route('/job-redirect')
def job_redirect():
    job_id = request.values.get('job_id')
    return redirect(url_for('job', job_id=job_id))


@app.route('/job')
def job_list():
    return render_template('job_list.html')


@app.route('/job/clear', methods=['POST'])
def clean_job():
    # Clear redis
    redis = RedisClient().get_instance()
    redis.flushdb()
    # Remove old files
    upload_dir = app.config['UPLOAD_FOLDER']
    for f in os.listdir(upload_dir):
        os.remove(os.path.join(upload_dir, f))

    return redirect(url_for('job_list'))


@app.route('/job/update')
def update_jobs():
    redis = RedisClient.get_instance()
    jobs = []
    for h in redis.keys():
        jb = redis.hgetall(h)
        jb['id'] = h
        jobs.append(jb)

    jobs = sorted(jobs, key=lambda j: j.get('start', 0), reverse=True)
    for jb in jobs:
        jb['start'] = datetime.fromtimestamp(float(jb['start'])).strftime('%Y-%m-%d %H:%M:%S')
        jb['complete'] = round(float(jb.get('progress', 0)) / float(jb['size']) * 100, 0) if float(jb['size']) else 0
        jb['finish'] = int(jb['finish']) == 1
        jb['user_file'] = build_user_filename(jb['file'])

    return jsonify(jobs=jobs)


def _process_job(job_id, keywords, output_file, upload_folder):
    redis = RedisClient.get_instance()
    redis.hset(job_id, 'size', len(keywords))
    redis.hset(job_id, 'start', time.time())
    redis.hset(job_id, 'file', output_file)
    redis.hset(job_id, 'finish', 0)
    kw_cleaner = KeywordCleaner(job_id)
    result = kw_cleaner.process_batch(keywords)
    try:
        with codecs.open(os.path.join(upload_folder, output_file), 'w', encoding='utf-8') as f:
            columns = ('Original Input', 'Cleaned Output', 'Character Count', 'Word Count')
            f.write('\t'.join(columns) + '\n')
            for item in result:
                row = (item['original'], item['cleaned'], str(item['char_count']), str(item['word_count']))
                f.write('\t'.join(row) + '\n')

        redis.hset(job_id, 'finish', 1)
    except Exception as e:
        logger.exception(e)


@app.route('/download/<filename>')
def download_file(filename):
    print filename
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True,
                               attachment_filename=build_user_filename(filename))


def build_user_filename(filename):
    return '_'.join(filename.split('_')[:-2]) + '-cleaned.txt'
