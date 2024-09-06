import json
from pathlib import Path


def process_file(file: Path):
    with file.open('rt', encoding=ENCODING) as f:
        text: str = f.read()

    result: list[dict] = list()
    content: list[str] = text.split('\n')

    for index, line in enumerate(content):
        lrc_list: list[str] = line.strip().split(']')

        time = lrc_list[0].replace('[', '')
        time = time.split(':')

        minute = int(time[0])
        total_seconds = minute * 60 + float(time[1])
        total_seconds = float(total_seconds)

        result.append({
            "time": total_seconds,
            "text": lrc_list[1],
        })

    length: int = len(result)

    for index, item in enumerate(result):
        for i in range(index + 1, length):
            if item['time'] == result[i]['time']:
                result[index]['ex'] = result[i]['text']
                result.pop(i)
                length -= 1
                break

    if MODE == 'replace':
        output_file = file.with_suffix('.json')
        file.unlink()
    else:
        output_file = OUTPUT_DIR.joinpath(file.name).with_suffix('.json')

    with output_file.open('wt', encoding=ENCODING) as f:
        json.dump(dict(lyric=result), f, ensure_ascii=False)


def main():
    all_files = INPUT_DIR.glob('*.lrc')
    for file in all_files:
        if file.is_file():
            process_file(file)


if __name__ == '__main__':
    ROOT = Path('./workplace')
    ROOT.mkdir(exist_ok=True)

    CONFIG_FILE = ROOT / 'config.json'
    CONFIG_FILE.touch()

    with CONFIG_FILE.open('rt+', encoding='utf-8') as f:
        try:
            config: dict[str, str] = json.load(f)
        except json.decoder.JSONDecodeError:
            config = dict()

        ENCODING: str = config.setdefault('encoding', 'utf-8')
        MODE: str = config.setdefault('mode', 'new')
        INPUT_DIR: Path = ROOT / config.setdefault('input_dir', './ly_input')
        OUTPUT_DIR: Path = ROOT / config.setdefault('output_dir', './ly_output')

        if MODE == 'replace' and input(
                '注意, 您选择了替换模式, 此模式可能导致意外的风险, 您确认开启吗: (Y/n): ').lower() == 'y':
            print('替换模式已启动')
        elif MODE != 'new':
            config['mode'] = 'new'
            MODE = 'new'

        f.seek(0)
        f.truncate()
        json.dump(config, f, indent=4, ensure_ascii=False)

    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    main()
