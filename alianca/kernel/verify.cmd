# verify.cmd — comando de constatacao DESTE harness (lido pelo Stop hook verify.py).
#
# verify.py NAO executa este arquivo como batch: ele le a PRIMEIRA linha
# nao-comentario (nao iniciada por '#') e a roda via shell, com cwd = raiz do
# projeto. Por isso NADA de '@echo off' aqui (viraria o comando executado) —
# apenas comentarios '#' e, abaixo, a UNICA linha de comando.
#
# Efeito: quando o proprio harness alegar "pronto", o terceiro portao roda o
# self-test do kernel e le o exit code real. O kernel se verifica a si mesmo.
python "alianca/kernel/selftest.py"
