import json
from os import system
from pathlib import Path


def process_file(file: Path, encoding: str, mode: str, output_dir: Path):
    try:
        with file.open('rt', encoding=encoding) as f:
            text: str = f.read()
    except Exception as e:
        print(f"Error reading file {file}: {e!r}")
        return

    result: list[dict[str, str]] = []
    content: list[str] = text.splitlines()

    for line in content:
        lrc_list: list[str] = line.strip().split(']')
        if len(lrc_list) < 2:
            continue

        time_str: str = lrc_list[0].replace('[', '')

        try:
            minute, second = map(float, time_str.split(':'))
        except ValueError:
            continue

        total_seconds: float = minute * 60 + second

        result.append({
            "time": total_seconds,
            "text": lrc_list[1],
        })

    length: int = len(result)

    for index in range(length):
        for i in range(index + 1, length):
            if result[index].get('time') == result[i].get('time'):
                result[index]['ex'] = result[i]['text']
                result.pop(i)
                length -= 1
                break

    output_file: Path = file.with_suffix('.json') if mode == 'replace' else output_dir / file.with_suffix('.json').name
    try:
        with output_file.open('wt', encoding=encoding) as f:
            f.write(json.dumps({"lyric": result}, ensure_ascii=False))

    except Exception as e:
        print(f"Error writing to file {output_file}: {e!r}")


def main():
    root: Path = Path('./lyric_workplace')
    root.mkdir(exist_ok=True)

    config_file: Path = root / 'config.json'
    config_file.touch()

    with config_file.open('rb+') as f:
        try:
            config: dict[str, str] = json.load(f)
        except json.decoder.JSONDecodeError:
            config: dict[str, str] = {}

        encoding: str = config.setdefault('encoding', 'utf-8')
        mode: str = config.setdefault('mode', 'new')
        input_dir: Path = root / config.setdefault('input_dir', './input')
        output_dir: Path = root / config.setdefault('output_dir', './output')

        if mode == 'replace' and input(
                '注意, 您选择了替换模式, 此模式可能导致意外的风险, 您确认开启吗: (Y/n): ').lower() != 'y':
            mode = 'new'
            config['mode'] = 'new'

        f.seek(0)
        f.truncate()
        f.write(json.dumps(config, indent=4, ensure_ascii=False).encode())

    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    count: int = 0
    for file in input_dir.glob('*.lrc'):
        if file.is_file():
            count += 1
            process_file(file, encoding, mode, output_dir)

    print(f'共处理 {count} 个文件')
    system('pause')


if __name__ == '__main__':
    main()
