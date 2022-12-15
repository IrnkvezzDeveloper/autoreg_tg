from telethon import TelegramClient
import config
import asyncio
import json
import os
from telethon.errors import PhoneNumberBannedError, PhoneNumberInvalidError


class UserExists(BaseException):
    ...


def ReadNumbersFile() -> list:
    try:
        return json.loads(open("numbers.json").read())
    except Exception:
        print("U need to generate numbers list!!!")


def main() -> None:
    work_type = int(
        input("Input work type\n\t1 - Single account\n\t2 - Account list\n\t3 - Generate numbers file(first use recomended)\n>> "))
    if work_type == 1:
        number = input("Input number >> ")
        first_name = input("Input first name for this account >> ")
        last_name = input("Input last name for this account >> ")
        autoreg = Autoregister()
        print(autoreg.AuthMainAccount())
        autoreg.AddNumberToRegistration(
            {'number': number, 'first_name': first_name, 'last_name': last_name})
        autoreg.StartRegistrations()
    elif work_type == 2:
        numbers = ReadNumbersFile()
        autoreg = Autoregister()
        for i in numbers:
            autoreg.AddNumberToRegistration(i)
        autoreg.StartRegistrations()
    elif work_type == 3:
        acc_count = int(input("Input u accounts count >> "))
        numbers = []
        for i in range(acc_count):
            number = input(f"[{i+1}] Input number >> ")
            first_name = input(
                f"[{i+1}] Input first name for this account >> ")
            last_name = input(f"[{i+1}] Input last name for this account >> ")
            data = {
                "number": number,
                "first_name": first_name,
                "last_name": last_name
            }
            numbers.append(data)

        with open("numbers.json", 'w') as fp:
            fp.write(json.dumps(numbers, ensure_ascii=False, indent=4))

        os.system("clear")
        print(f"Accounts file generated. Data count: {len(numbers)}")


class Autoregister:
    def __init__(self):
        self.numbers = []
        self.main_acc: TelegramClient = None
        self.reg_acc: TelegramClient = None
        self.ret = None

    def AddNumberToRegistration(self, number: dict) -> None:
        self.numbers.append(number)
        print(f"Number {number['number']} added to registration list")

    def AuthMainAccount(self) -> None:
        self.main_acc = self.AuthAccount("main", config.main_acc_number, True)

    def AuthAccount(self, session_name: str, number: str, is_local: bool) -> TelegramClient:
        async def asyncio_wrapper():
            temp = TelegramClient(
                session_name, api_hash=config.api_hash, api_id=config.api_id)
            self.ret = temp
            await temp.connect()
            if not await temp.is_user_authorized():
                await temp.send_code_request(number)
                try:
                    if is_local:
                        await temp.sign_in(number, input("Input code >> "))
                        print("Log in successfully")
                    else:
                        # await temp.sign_up
                        ...
                except Exception as ex:
                    print(ex)

        asyncio.run(asyncio_wrapper())
        return self.ret

    def RegisterAccount(self, session_name: str, data: dict) -> bool:  # return true or false
        async def asyncio_wrapper():
            temp = TelegramClient(
                session_name, api_hash=config.api_hash, api_id=config.api_id)
            await temp.connect()
            if not await temp.is_user_authorized():
                try:
                    await temp.send_code_request(data['number'])
                    # TODO complete scrape code for service
                    await temp.sign_up(123123, data['first_name'], data['last_name']. data['phone'])
                    print("Account registred")
                    return True
                except PhoneNumberBannedError as bp:
                    print(f"Number {data['number']} is banned. Skipping...")
                    print(bp)
                    return False
                except PhoneNumberInvalidError:
                    print(f"Number {data['number']} is invalid")
                    return False

        asyncio.run(asyncio_wrapper())

    def StartRegistrations(self):
        for i in self.numbers:
            self.RegisterAccount(
                f"./sessions/{i['number']}_{i['first_name']}_{i['last_name']}", i)


if __name__ == '__main__':
    main()
