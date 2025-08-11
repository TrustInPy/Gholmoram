import sqlite3
import threading
from .. import QueryBundle


class SqliteInterface:
    """Sync version of SqliteInterface"""

    def __init__(
        self, data_filepath: str, readonly: bool = False, use_foreign_keys: bool = False
    ):
        self.__readonly = readonly
        self.__con = sqlite3.Connection(data_filepath, check_same_thread=False)
        if use_foreign_keys:
            self.__con.execute("PRAGMA foreign_keys = ON;")
        self.__cur = self.__con.cursor()
        self.__write_lock = threading.Lock()

    def close(self):
        self.__con.close()

    def execute(
        self,
        query: str,
        params: tuple = None,
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
        force_consistency: bool = False,
    ):
        should_lock = commit or force_consistency
        if should_lock:
            with self.__write_lock:
                return self.__execute(
                    query=query,
                    params=params,
                    is_many=False,
                    commit=commit,
                    fetchone=fetchone,
                    fetchall=fetchall,
                )
        else:
            return self.__execute(
                query=query,
                params=params,
                is_many=False,
                commit=commit,
                fetchone=fetchone,
                fetchall=fetchall,
            )

    def executemany(
        self,
        query: str,
        params_list: list[tuple] = [],
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
        force_consistency: bool = False,
    ):
        should_lock = commit or force_consistency
        if should_lock:
            with self.__write_lock:
                return self.__execute(
                    query=query,
                    params=params_list,
                    is_many=True,
                    commit=commit,
                    fetchone=fetchone,
                    fetchall=fetchall,
                )
        else:
            return self.__execute(
                query=query,
                params=params_list,
                is_many=True,
                commit=commit,
                fetchone=fetchone,
                fetchall=fetchall,
            )

    def __execute(
        self,
        query: str,
        params,
        is_many: bool = False,
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
    ):
        if commit and self.__readonly:
            raise Exception(
                "This sqlite3 interface instance is marked as readonly "
                + "and cannot perform this operation."
            )
        result = None
        if is_many:
            self.__cur.executemany(query, params)
        else:
            self.__cur.execute(query, params)
        if commit:
            self.__con.commit()
        if fetchone:
            result = self.__cur.fetchone()
        elif fetchall:
            result = self.__cur.fetchall()
        return result

    async def execute_transaction(self, query_bundles: list[QueryBundle]):
        with self.__write_lock:
            try:
                for query_bundle in query_bundles:
                    if query_bundle.params and len(query_bundle.params) > 1:
                        # many
                        params_list: list[tuple] = query_bundle.params
                        self.executemany(query_bundle.query, params_list)
                    else:
                        # single
                        params: tuple | None = (
                            query_bundle.params[0]
                            if (query_bundle.params and len(query_bundle) > 0)
                            else None
                        )
                        self.execute(query_bundle.query, params)
                self.__con.commit()
            except:
                self.__con.rollback()
                raise
