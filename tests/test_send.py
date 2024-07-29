import os

from deltawoot.send import download_file


def test_download_file(tmp_path):
    os.chdir(tmp_path)
    url = "https://ru.wikipedia.org/wiki/%D0%9B%D0%B8%D1%88%D0%B0%D0%BA,_%D0%A5%D0%B8%D0%BB%D1%8C%D0%B4%D0%B0#/media/%D0%A4%D0%B0%D0%B9%D0%BB:%D0%A5%D0%B8%D0%BB%D1%8C%D0%B4%D0%B0_1.png"
    filename = download_file(url)
    assert "files" in filename
    assert "attachments" in filename
    assert filename != os.getcwd() + "/Файл:Хильда_1.png"
    assert filename.split("/")[-1] == "Файл:Хильда_1.png"
    assert os.path.getsize(filename) == 276881
