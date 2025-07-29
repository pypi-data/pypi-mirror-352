# netkeiber

Collect data from netkeiba.com

## chromeバージョン確認

>google-chrome --version

## webDriverパーミッション変更

>sudo chmod 755 webDriver/chrome/linux/chromedriver

## chromeバージョンアップ

>sudo apt update
>sudo apt upgrade

以下のエラーが発生する場合
The following signatures couldn't be verified because the public key is not available: NO_PUBKEY [キー]

## aptのkeyマネージャーに登録

>sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys [キー]

32EE5355A6BC6E42
