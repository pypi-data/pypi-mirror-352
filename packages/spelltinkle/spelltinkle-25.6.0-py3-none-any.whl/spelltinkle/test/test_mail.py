import stat
from pathlib import Path


def test_jjmail(run):
    run.conf.mail = {'smoerhul': {'host': 'imap.one.com',
                                  'user': 'jj@smoerhul.dk'}}
    mail = run.conf.home / 'mail'
    test = mail / 'smoerhul'
    test.mkdir(parents=True)
    pw = test / 'pw'
    pw.write_text((Path.home() / '.spelltinkle/mail/smoerhul/pw').read_text())
    pw.chmod(stat.S_IRUSR | stat.S_IWUSR)
    (mail / 'addresses.csv').write_text('Sloof Lirpa <test@test.org>, test\n')
    run('^vmr')
    print(run.lines)
    run.doc.enter()
