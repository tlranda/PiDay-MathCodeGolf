try:
  from mpmath import mp
except ImportError as e:
  print("Try `pip3 install --user mpmath`, then rerun")
  raise e
char_limit = 1024
req_char="/10**"
with open('ans.txt', 'w') as f:
  m=char_limit-len(req_char) # Number of characters we have in budget - ALWAYS written characters
  m-=len(str(m-2)) # Subtract the number of digits it takes to write the power
  mp.dps=m # Set mpmath to generate this many digits of pi
  x = mp.pi
  c = 1
  while c<m:
    f.write(str(int(x))) # Write current digit
    # Generate next digit
    x -= int(x)
    x *= 10
    c += 1
  # Write trailing divisor and power
  f.write(f"{req_char}{int(m-2)}\n")

