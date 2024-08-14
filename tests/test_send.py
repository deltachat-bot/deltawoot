import os

from deltawoot.send import download_file


def test_download_file(tmp_path):
    os.chdir(tmp_path)
    url = "https://upload.wikimedia.org/wikipedia/commons/5/51/%D0%A5%D0%B8%D0%BB%D1%8C%D0%B4%D0%B0_1.png"
    filename = download_file(url)
    assert "files" in filename
    assert "attachments" in filename
    assert filename != os.getcwd() + "/Хильда_1.png"
    assert filename.split("/")[-1] == "Хильда_1.png"
    assert os.path.getsize(filename) == 259471
