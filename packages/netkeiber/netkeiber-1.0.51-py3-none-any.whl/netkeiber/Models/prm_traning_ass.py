import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class prm_traning_ass(Base):
	
	# テーブル名
	__tablename__ = 'prm_traning_ass'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	race_id = fld.CharFields(12,primary_key=True,default='')
	horse_no = fld.NumericFields(2,0,primary_key=True,default=0)
	assessment_jp = fld.CharFields(50,default='')
	assessment_al = fld.CharFields(1,default='')
	updinfo = fld.CharFields(40,default='')
