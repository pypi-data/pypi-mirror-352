import argparse

from utils_hj3415 import tools
from scraper_hj3415 import nfs


def db_manager():
    parser = argparse.ArgumentParser(description="데이터베이스 주소 관리 프로그램")
    db_subparsers = parser.add_subparsers(dest='db_type', help='데이터베이스 종류를 지정하세요(mongo, redis)', required=True)

    # 'mongo' 명령어 서브파서
    mongo_parser = db_subparsers.add_parser('mongo', help=f"mongodb 데이터베이스")
    mongo_subparser = mongo_parser.add_subparsers(dest='command', help='mongodb 데이터베이스 관련된 명령')

    # mongo - repair 파서
    mongo_repair_parser = mongo_subparser.add_parser('repair', help=f"mongodb의 모든 종목의 컬렉션 유효성을 확인하고 없으면 채웁니다.")
    mongo_repair_parser.add_argument('targets', nargs='*', type=str, help="대상 종목 코드를 입력하세요. 'all'을 입력하면 전체 종목을 대상으로 합니다.")

    # 'redis' 명령어 서브파서
    redis_parser = db_subparsers.add_parser('redis', help=f"redis 데이터베이스")
    redis_subparser = redis_parser.add_subparsers(dest='command', help='redisdb 데이터베이스 관련된 명령')

    # redis - delete 파서
    redis_delete_parser = redis_subparser.add_parser('delete')
    redis_delete_parser.add_argument('redis_name', type=str, help="레디스키 또는 all")

    # redis - delete 파서
    redis_list_parser = redis_subparser.add_parser('list')
    redis_list_parser.add_argument('targets', type=str, help="대상 종목 코드를 입력하세요. 'all'을 입력하면 전체 종목을 대상으로 합니다.")

    args = parser.parse_args()

    if args.db_type in ['mongo', 'redis']:
        if args.db_type == 'mongo' and args.command == 'repair':
            from db_hj3415 import mymongo
            if len(args.targets) == 1 and args.targets[0] == 'all':
                all_codes_in_db = mymongo.Corps.list_all_codes()
                print(f"**** 모든 종목({len(all_codes_in_db)})의 데이터베이스를 검사합니다. ****")
                mymongo.Logs.save('cli','INFO','run >> db mongo repair all')
                missing_dict = mymongo.Corps.chk_integrity(*all_codes_in_db)
            else:
                # 입력된 종목 코드 유효성 검사
                invalid_codes = [code for code in args.targets if not tools.is_6digit(code)]
                if invalid_codes:
                    print(f"다음 종목 코드의 형식이 잘못되었습니다: {', '.join(invalid_codes)}")
                    return
                print(f"**** {args.targets} 종목의 데이터베이스를 검사합니다. ****")
                missing_dict = mymongo.Corps.chk_integrity(*args.targets)

            repairable_codes = list(missing_dict.keys())
            if len(repairable_codes) != 0:
                print(f"**** {repairable_codes} 종목에서 이상이 발견되어서 스크랩하겠습니다. ****")
                mymongo.Logs.save('cli','WARNING', f'mongo repair - {repairable_codes}')
                nfs.all_spider(*repairable_codes)
        elif args.db_type == 'redis':
            from db_hj3415 import myredis
            base = myredis.Base()
            if args.command == 'delete':
                if args.redis_name == 'all':
                    for redis_name in base.list_redis_names():
                        print(redis_name)
                    print(f"총 {len(base.list_redis_names())}개의 캐시를 삭제했습니다.")
                    myredis.Base.delete_all_with_pattern('*')
            elif args.command == 'list':
                for redis_name in base.list_redis_names(filter=args.targets):
                    print(redis_name.decode('utf-8'))
        else:
            parser.print_help()
    else:
        parser.print_help()
