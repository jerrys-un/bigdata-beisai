#!/bin/bash
# ============================================================================
# 学习站账号管理（nginx Basic Auth —— 服务端校验，输错进不来）
# 部署位置：/data/study-site/study-users.sh
#
#   ./study-users.sh add   用户名 口令    新增 / 改口令（同名覆盖）
#   ./study-users.sh del   用户名        删除账号
#   ./study-users.sh list                列出已有账号
#   ./study-users.sh on                  开启密码保护
#   ./study-users.sh off                 关闭密码保护（机房内网自用时可关）
#   ./study-users.sh status              看当前是开着还是关着
#
# 说明：
#   · 口令用 APR1 哈希存进 .htpasswd，看不到明文
#   · 站点是 http，口令在局域网内明文传输（base64），仅限内网使用
#   · 账号只管「能不能进站」；学习进度靠网页右上角的「使用者」按名字分开存
# ============================================================================
set -e
D=/data/study-site
CONF=$D/nginx.conf
OPEN=$D/nginx-open.conf
AUTH=$D/nginx-auth.conf
PW=$D/.htpasswd

case "$1" in

  add)
    U="$2"; P="$3"
    if [ -z "$U" ] || [ -z "$P" ]; then
      echo "用法：$0 add 用户名 口令"; exit 1
    fi
    [ -f "$PW" ] || touch "$PW"
    grep -v "^$U:" "$PW" > "$PW.tmp" 2>/dev/null || true
    mv "$PW.tmp" "$PW"
    echo "$U:$(openssl passwd -apr1 "$P")" >> "$PW"
    chmod 644 "$PW"
    echo "已设置账号：$U"
    docker restart study-site >/dev/null 2>&1 || true
    ;;

  del)
    U="$2"
    if [ -z "$U" ]; then echo "用法：$0 del 用户名"; exit 1; fi
    [ -f "$PW" ] || { echo "还没有账号"; exit 0; }
    grep -v "^$U:" "$PW" > "$PW.tmp" 2>/dev/null || true
    mv "$PW.tmp" "$PW"
    echo "已删除账号：$U"
    docker restart study-site >/dev/null 2>&1 || true
    ;;

  list)
    if [ ! -s "$PW" ]; then echo "（暂无账号）"; exit 0; fi
    echo "已有账号："
    cut -d: -f1 "$PW"
    ;;

  on)
    [ -f "$PW" ] || touch "$PW"
    chmod 644 "$PW"
    cp "$AUTH" "$CONF"
    docker restart study-site >/dev/null
    echo "已开启密码保护：进站需要输入账号密码"
    ;;

  off)
    cp "$OPEN" "$CONF"
    docker restart study-site >/dev/null
    echo "已关闭密码保护：局域网内可直接访问"
    ;;

  status)
    if grep -q auth_basic "$CONF" 2>/dev/null; then
      echo "状态：密码保护【已开启】  账号数：$( [ -f "$PW" ] && wc -l < "$PW" || echo 0 )"
    else
      echo "状态：密码保护【已关闭】"
    fi
    ;;

  *)
    sed -n '3,20p' "$0" | sed 's/^# \{0,1\}//'
    ;;
esac
