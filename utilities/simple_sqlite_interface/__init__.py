import aiosqlite
import sqlite3
import threading


class QueryBundle:
    def __init__(self, query: str, params, is_many: bool = False):
        self.query = query
        self.params = params
        self.is_many = is_many


class SqliteInterface:
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
        params: tuple = (),
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
        force_consistency: bool = False,
    ):
        return self.__execute(
            query=query,
            params=params,
            is_many=False,
            commit=commit,
            fetchone=fetchone,
            fetchall=fetchall,
            force_consistency=force_consistency,
        )

    def executemany(
        self,
        query: str,
        params_seq: list = [],
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
        force_consistency: bool = False,
    ):
        return self.__execute(
            query=query,
            params=params_seq,
            is_many=True,
            commit=commit,
            fetchone=fetchone,
            fetchall=fetchall,
            force_consistency=force_consistency,
        )

    def __execute(
        self,
        query: str,
        params: list = [],
        is_many: bool = False,
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
        force_consistency: bool = False,
    ):
        should_lock = commit or force_consistency
        if commit and self.__readonly:
            raise Exception(
                "This sqlite3 interface is marked as readonly "
                + "and cannot perform this operation."
            )
        try:
            result = None
            if should_lock:
                self.__write_lock.acquire()
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
            if should_lock:
                self.__write_lock.release()
            return result
        except:
            raise
        finally:
            try:
                if should_lock:
                    self.__write_lock.release()
            except:
                pass

    def execute_transaction(self, query_bundles: list[QueryBundle]):
        try:
            for query_bundle in query_bundles:
                if query_bundle.is_many:
                    self.executemany(query_bundle.query, query_bundle.params)
                else:
                    self.execute(query_bundle.query, query_bundle.params)
            self.__con.commit()
        except:
            self.__con.rollback()
            raise


class AsyncSqliteInterface:
    async def __init__(
        self, data_filepath: str, readonly: bool = False, use_foreign_keys: bool = False
    ):
        self.__readonly = readonly
        self.__con = aiosqlite.connect(data_filepath, check_same_thread=False)
        if use_foreign_keys:
            await self.__con.execute("PRAGMA foreign_keys = ON;")
        self.__cur = await self.__con.cursor()
        self.__write_lock = threading.Lock()

    async def close(self):
        await self.__con.close()

    async def execute(
        self,
        query: str,
        params: tuple = (),
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
        force_consistency: bool = False,
    ):
        return await self.__execute(
            query=query,
            params=params,
            is_many=False,
            commit=commit,
            fetchone=fetchone,
            fetchall=fetchall,
            force_consistency=force_consistency,
        )

    async def executemany(
        self,
        query: str,
        params_seq: list = [],
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
        force_consistency: bool = False,
    ):
        return await self.__execute(
            query=query,
            params=params_seq,
            is_many=True,
            commit=commit,
            fetchone=fetchone,
            fetchall=fetchall,
            force_consistency=force_consistency,
        )

    async def __execute(
        self,
        query: str,
        params: list = [],
        is_many: bool = False,
        commit: bool = False,
        fetchone: bool = False,
        fetchall: bool = False,
        force_consistency: bool = False,
    ):
        should_lock = commit or force_consistency
        if commit and self.__readonly:
            raise Exception(
                "This sqlite3 interface is marked as readonly "
                + "and cannot perform this operation."
            )
        try:
            result = None
            if should_lock:
                self.__write_lock.acquire()
            if is_many:
                await self.__cur.executemany(query, params)
            else:
                await self.__cur.execute(query, params)
            if commit:
                await self.__con.commit()
            if fetchone:
                result = await self.__cur.fetchone()
            elif fetchall:
                result = await self.__cur.fetchall()
            if should_lock:
                self.__write_lock.release()
            return result
        except:
            raise
        finally:
            try:
                if should_lock:
                    self.__write_lock.release()
            except:
                pass

    async def execute_transaction(self, query_bundles: list[QueryBundle]):
        try:
            for query_bundle in query_bundles:
                if query_bundle.is_many:
                    await self.executemany(query_bundle.query, query_bundle.params)
                else:
                    await self.execute(query_bundle.query, query_bundle.params)
            await self.__con.commit()
        except:
            await self.__con.rollback()
            raise
