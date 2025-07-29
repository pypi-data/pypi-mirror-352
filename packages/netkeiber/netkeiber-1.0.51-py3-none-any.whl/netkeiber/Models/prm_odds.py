import LibHanger.Models.modelFields as fld
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import Null

# Baseクラス生成
Base = declarative_base()

class prm_odds(Base):
	
	# テーブル名
	__tablename__ = 'prm_odds'
	
	# スキーマ
	__table_args__ = {'schema': 'nkaz'}
	
	# 列定義
	race_id = fld.CharFields(12,primary_key=True,default='')
	horse_no = fld.NumericFields(2,0,primary_key=True,default=0)
	get_datetime = fld.DateTimeFields(primary_key=True,default=Null)
	win_odds = fld.NumericFields(5,2,default=0)
	popular = fld.NumericFields(2,0,default=0)
	updinfo = fld.CharFields(40,default='')
