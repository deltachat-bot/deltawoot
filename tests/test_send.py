import os

from deltawoot.send import download_file


def test_download_file(tmp_path):
    os.chdir(tmp_path)
    url = "https://delta.chat/assets/logos/delta-chat.svg"
    filename = download_file(url)
    assert "files" in filename
    assert "attachments" in filename
    assert filename != os.getcwd() + "/delta-chat.svg"
    assert os.path.getsize(filename) == 1868
