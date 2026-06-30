# Hava Nedir
hava kısaca pythonda hobi amaçlı geliştirilmiş multi-dil grameri olan ilginç bir programlama dilidir

# nasıl çalışıyor
.hava dosyasına veya repl a fark etmez, kodu yazarsınız ve bu kod ilk başta tokenlarına ayrılır. 

örneğin:
```
yaz("hava"):
```
```
NAME(yaz)
(
STRING(hava)
)
FINISH_PREFIX(:)
```
bunu yapana lexer denir. buradaki name,string,finish_prefix önceden lexerda belirlenmiş kurallar tarafından sağlanır.
```
    @_(r"[a-zA-ZğüşöçıİĞÜŞÖÇ_][a-zA-Z0-9ğüşöçıİĞÜŞÖÇ_]*")
    def NAME(self, t):
        ...
    
    
    @_(r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'')
    def STRING(self, t):
        ...
```

```
    @_('NAME')
    def expr(self, p):
        return 'var', p.NAME

    @_('STRING')
    def expr(self, p):
        return 'str', p.STRING
```
bu tokenler parsera gider, parser tokenlara bakar, sonra der ki 
STRING("hava") `expr` olabilir
ast ağacına `('str', 'hava')` böyle girer
NAME(yaz) `expr` olabilir
ast ağacına `('var', 'yaz')` böyle girer ama bununla aşağıdaki vereceğim örneklerde pek işimiz yok, çünkü bunu expr olarak kullanmayacağız. 
evet NAME(yaz) bir expr olabilir fakat bu sadece onun expr olarak kullanıldığı yerlerde geçerlidir. `NAME(yaz)` parser’a ilk geldiğinde dümdüz bir NAME tokenıdır, parser bu tokeni bulunduğu yere göre yorumlar.

```
    @_('NAME "(" args ")"')
    def expr(self, p):
        return 'fun_call', p.NAME, p.args
```
`yaz("hava")` `expr` olabilir
yani bütün kod parçası `expr` oldu
ast ağacına `('fun_call', 'yaz', [('str', 'hava')])` şeklinde yerleşecek
not: eğerki kuralda `NAME` yerine `expr` yazsaydık o zaman ast ağacına `('fun_call', 'yaz', [('str', 'hava')])` yerine `('fun_call', ('var', 'yaz'), [('str', 'hava')])` olarak girerdi.
aslında ileride `NAME` yerine `expr` kullanmayı planlıyorum, `NAME` kullanmam array veya dict `array[0]()` üzerinden fonksiyon çağırmamı veya `get_func` gibi fonksiyon yapmamı engelliyor fakat bunun için parser dışında compiler ve VM tarafında da `CALL` mantığını değiştirmek gerekir o yüzden sonra bakacağım

```
    @_('expr FINISH_PREFIX')
    def statement(self, p):
        return 'expr_stmt', p.expr
```
bu sayede bu kod parçasına tam anlamıyla uyum sağladı:
`yaz("hava")` -> `expr`
`FINISH_PREFIX` -> `FINISH_PREFIX`
yani
`('fun_call', 'yaz', [('str', 'hava')])` `statement` olabilir
ast ağacına `('expr_stmt', ('fun_call', 'yaz', [('str', 'hava')]))` şeklinde yerleşecek

```
    @_('statement')
    def statements(self, p):
        return [p.statement]
```
`yaz("hava"):` en son komple `statement` olduğundan bu kod parçasına da uyum sağlar ve sonuç olarak `('expr_stmt', ('fun_call', 'yaz', [('str', 'hava')]))` bir `statements` olabilir
ast ağacına `[('expr_stmt', ('fun_call', 'yaz', [('str', 'hava')]))]` şeklinde yerleşecek
```
    @_('statements')
    def program(self, p):
        return 'program', p.statements
```
en sonunda `start = 'program'`, parser’ın en dışta hangi grammar kuralını bekleyeceğini belirliyor. bu sayede parser bütün dosyayı bir program olarak okumaya çalışır.

eğer komple grameri değiştirme kararı almadıysam şöyle duracak:
```
(
    'program',
    [
        ('expr_stmt', ('fun_call', 'yaz', [('str', 'hava')]))
    ]
)
```