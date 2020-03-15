from database import db


class User(db.Model):
    """Represents Proected users."""

    # Set the name for table
    __tablename__ = 'users'
    # 如果使用自增字段不要使用init函数
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    docs = db.relationship(
        'JudicialDoc',
        backref='users',
        lazy='dynamic')
    tasks = db.relationship(
        'Task',
        backref='users',
        lazy='dynamic')
    config = db.relationship(
        'Config',
        backref='users',
        lazy='dynamic')

    # def __repr__(self):
    #     """Define the string format for instance of User."""
    #     return "<Model User `{}`>".format(self.username)

#
# tasks_docs = db.Table('tasks_docs',
#     db.Column('task_id', db.String(45), db.ForeignKey('tasks.id')),
#     db.Column('doc_id', db.String(45), db.ForeignKey('judicial_docs.id')))
#


class JudicialDoc(db.Model):
    """Represents judicial documents."""

    # Set the name for table
    __tablename__ = 'judicial_docs'
    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    task_id = db.Column(db.Integer,db.ForeignKey('tasks.id'))
    docname = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    check_status = db.Column(db.Enum('untested','waiting','testing','finished','wrong','accident'), nullable=False)
    length = db.Column(db.INTEGER, nullable=False)
    loc = db.Column(db.String(200), nullable=False)
    province = db.Column(db.String(10))
    writ_date = db.Column(db.String(10))
    reports = db.relationship(
        'Report',
        backref='judicial_docs',
        lazy='dynamic')
    # docs = db.relationship(
    #     'Task',
    #     secondary=tasks_docs,
    #     backref=db.backref('judicial_docs', lazy='dynamic'))

    # def __repr__(self):
    #     """Define the string format for instance of JudicialDoc."""
    #     return "<Model JudicialDoc `{}`>".format(self.file_name)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    progress_status = db.Column(db.Enum('untested','waiting','testing','finished','wrong','accident'), nullable=False)
    analysis_report = db.relationship(
        'AnalysisReport',
        backref='tasks',
        lazy='dynamic')
    docs = db.relationship(
        'JudicialDoc',
        backref='tasks',
        lazy='dynamic')

# class TaskFile(db.Model):
#     __tablename__ = 'task_file'
#     task_file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
#     file_id = db.Column(db.Integer, db.ForeignKey('judicial_docs.id'))


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.String(50), primary_key=True)
    doc_id = db.Column(db.String(50), db.ForeignKey('judicial_docs.id'))
    loc = db.Column(db.String(200), nullable=False)


class AnalysisReport(db.Model):
    __tablename__ = 'analysis_reports'
    id = db.Column(db.String(50), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    loc = db.Column(db.String(200), nullable=False)


class Config(db.Model):
    __tablename__ = 'configs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    config_json = db.Column(db.String(100), nullable=False)
