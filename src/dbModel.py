from API import db
class Alembic(db.Model):
    __tablename__ = 'alembic_version'
    version_num = db.Column(db.String(32), primary_key=True, nullable=False)

    @staticmethod
    def clear_A():
        for aa in Alembic.query.all():
            print (aa.version_num)
            db.session.delete(aa)
            db.session.commit()
            print ('======== data in Table: Alembic cleared!')
