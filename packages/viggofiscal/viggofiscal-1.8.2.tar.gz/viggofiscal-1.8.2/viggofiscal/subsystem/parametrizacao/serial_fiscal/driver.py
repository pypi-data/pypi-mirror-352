from sqlalchemy import func, select
from viggocore.common.subsystem import driver


class Driver(driver.Driver):

    def get_next_ultimo_doc(self, session, serie_fiscal_id):
        result = None
        get_next_ultimo_doc_func = func.serie_fiscal_next_ultimo_doc
        statement = select(get_next_ultimo_doc_func(serie_fiscal_id))
        row_tuple = session.execute(statement).first()
        if len(row_tuple) > 0:
            result = row_tuple[0]
        return result
