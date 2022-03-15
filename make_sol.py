from mpmath import mp
char_limit = 1024
req_char="/10**"
with open('ans.txt', 'w') as f:
  m=(char_limit-len(req_char))
  m-=len(str(m-2))
  mp.dps=m
  x = mp.pi
  c = 1
  while c<m:
    f.write(str(int(x)))
    x -= int(x)
    x *= 10
    c += 1
  f.write(f"{req_char}{int(m-2)}\n")
  #f.write("/1"+"0"*(m-2)+"\n")

