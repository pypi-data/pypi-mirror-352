import asyncio
import os
import time
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

import aiofiles


class Run:
    def __init__(self):
        self.py = Py()
        pass

    # * Shell
    async def shell_exec(
        command: str,
        executable: Optional[str] = None,
        timeout: Optional[Union[int, float]] = None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    ) -> Tuple[int, str, str]:
        process = await asyncio.create_subprocess_shell(
            cmd=command, stdout=stdout, stderr=stderr, shell=True, executable=executable
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
        except asyncio.exceptions.TimeoutError as e:
            process.kill()
            raise e

        return process.returncode, stdout.decode(), stderr.decode()

    async def gcc(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """C dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.c"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"gcc -o output {file_name}",
                timeout=timeout,
                executable=executable,
            )
            if rcode != 0:
                os.remove(file_name)
                return rcode, stdout, stderr
            rcode, stdout, stderr = await self.shell_exec(
                "./output",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def gpp(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """C++ dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.cpp"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"g++ -o output {file_name}",
                timeout=timeout,
                executable=executable,
            )
            if rcode != 0:
                os.remove(file_name)
                return rcode, stdout, stderr
            rcode, stdout, stderr = await self.shell_exec(
                "./output",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def lua(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Lua dili için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.lua"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"lua {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def go(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Go dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.go"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"go run {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def node(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Node.js için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.js"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"node {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def php(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """PHP dili için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.php"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"php {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def python(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Python dili için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.py"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"python {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def ruby(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Ruby dili için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.rb"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"ruby {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def perl(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Perl dili için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.pl"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"perl {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def bash(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Bash dili için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.sh"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"bash {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def swift(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Swift dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.swift"
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"swift {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def kotlin(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Kotlin dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.kt"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"kotlinc {file_name} -include-runtime -d output.jar && java -jar output.jar",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            os.remove("output.jar")
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def rust(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Rust dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.rs"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"rustc {file_name} -o output && ./output",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            os.remove("output")
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def java(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Java dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """
        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.java"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"javac {file_name} && java {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def csharp(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """C# dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """

        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.cs"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"mcs {file_name} && mono {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def scala(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Scala dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """

        try:
            file_name = f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.scala"
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"scalac {file_name} && scala {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def julia(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Julia dili için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """

        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.jl"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"julia {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def rlang(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """R dili için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """

        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.r"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"Rscript {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def groovy(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Groovy dili için verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Çalıştırma işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """

        try:
            file_name = f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.groovy"
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"groovy {file_name}",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def cobol(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """COBOL dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """

        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.cob"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"cobc -x {file_name} && ./a.out",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            os.remove("a.out")
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def dlang(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """D dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """

        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.d"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"dmd {file_name} && ./a.out",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            os.remove("a.out")
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def fortran(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Fortran dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """

        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.f90"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"gfortran {file_name} && ./a.out",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            os.remove("a.out")
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)

    async def ada(
        self,
        code: str,
        *,
        timeout: Optional[int] = 10,
        executable: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """Ada dili için verilen kodu derler ve çalıştırır.

        Args:
            code (str): Derlenecek kod.
            timeout (Optional[int], optional): Zaman aşımı. Defaults to 10.
            executable (Optional[str], optional): Derleme işlemi için kullanılacak komut. Defaults to None.

        Returns:
            Tuple[int, str, str]: Çıkış kodu, standart çıktı ve standart hata.
        """

        try:
            file_name = (
                f"{os.path.dirname(os.path.realpath(__file__))}/temp_{time.time()}.adb"
            )
            async with aiofiles.open(file_name, "w", encoding="utf-8") as f:
                await f.write(code)
                await f.close()
            rcode, stdout, stderr = await self.shell_exec(
                f"gcc {file_name} -o output && ./output",
                timeout=timeout,
                executable=executable,
            )
            os.remove(file_name)
            os.remove("output")
            return rcode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)


class Py:
    def __init__(self):
        pass

    async def run_command(
        self, cmd: List[str], return_time: bool = False
    ) -> Union[Tuple[str, str, None], Tuple[str, str, float], None]:
        """Verilen komutu çalıştırır.

        Args:
            cmd (List[str]): Çalıştırılacak komut.
            return_time (bool, optional): Zamanı döndürme. Defaults to False. 

        Returns:
            Union[Tuple[str, str, None], Tuple[str, str, float], None]: Çıktı, hata ve zaman.
            
        Example:
            .. code-block:: python

            async def main():
                run = Run()
                result, error, time = await run.run_command(["ls", "-l"], return_time=True)
                if error:
                    print(f"Error: {error}")
                else:
                    print(f"Result:\n{result}")
                    print(f"Time: {time}")

            if __name__ == "__main__":
                asyncio.run(main())
        """
        try:
            start_time = time.time()
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            end_time = time.time()
            if process.returncode != 0:
                raise Exception(f"Command failed with error: {stderr.decode()}")
            return (
                (stdout.decode(), stderr.decode(), None)
                if not return_time
                else (stdout.decode(), stderr.decode(), (end_time - start_time))
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, str(e), None

    # * Python Codes
    async def aexec(
        self,
        code: str,
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Union[str, None], str]:
        """Async olarak verilen kodu çalıştırır.

        Args:
            code (str): Çalıştırılacak kod.

        Returns:
            Tuple[Union[str, None], str]: Çıktı ve hata mesajı.

        Example:
            .. code-block:: python

            async def main():
                run = Run()
                code = '''
                key = kwargs.get("key")
                print(key)
                abc = args[0]
                print(abc)
                '''
                result, error = await run.aexec(
                    code,
                    "Hello, World!",
                    timeout=5,
                    key="value",
                )
                if error:
                    print(f"Error: {error}")
                else:
                    print(f"Result:\n{result}")

            if __name__ == "__main__":
                asyncio.run(main())
        """
        exec(
            "async def __todo(*args, **kwargs):\n"
            + "".join(f"\n {_l}" for _l in code.split("\n"))
        )

        f = StringIO()
        with redirect_stdout(f):
            try:
                if "timeout" in kwargs:
                    timeout = kwargs["timeout"]
                await asyncio.wait_for(
                    locals()["__todo"](*args, **kwargs),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                raise
            except Exception as e:
                return None, str(e)
            else:
                return f.getvalue(), None

    def async_wrap(self, func):
        async def wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)

        return wrapper
