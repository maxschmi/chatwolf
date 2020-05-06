import os
import re

files = os.listdir("chatwolf")[:-2]

for file in files:
    orig = open("chatwolf\\"+ file, "r").read()
    smat = re.search(r'["]{3}', orig)
    if smat:
        new = orig[:smat.span()[1]]
        end = -3
        while smat:
            start = smat.span()[1] + end + 3
            emat = re.search(r'["]{3}', orig[start:])
            if emat:
                end = emat.span()[0] + start
                docstr = orig[start:end]
                docstr = re.sub("\(default: \{", ". Defaults to ", docstr) 
                docstr = re.sub("\}\)", ".", docstr) 
                docstr = re.sub("{", "(", docstr)
                docstr = re.sub("}", ")", docstr)
                docstr = re.sub(" -- ", ": ", docstr)
                docstr = re.sub("Arguments:", "Args:", docstr)
                mkeyargs = re.search(r"(Keyword Args:)", docstr)
                if mkeyargs:
                    skeyargs = mkeyargs.span()[1]
                    mindent = re.search("[ ]+\n", docstr[:skeyargs][::-1])
                    num_indent = mindent.span()[1]-mindent.span()[0]-1
                    endkeyargs = re.search(r"\n[ ]{"+str(num_indent)+ r'}[a-zA-Z]+', docstr[skeyargs:])
                    if endkeyargs:
                        endkeyargs = endkeyargs.span()[0]+skeyargs
                    else:
                        endkeyargs = len(docstr)
                    keyargs = docstr[skeyargs:endkeyargs]
                    keyargs = re.sub(r"\):", r", optional):", keyargs)
                    docstr = docstr[:skeyargs] + keyargs + docstr[endkeyargs:]
                smat = re.search(r'["]{3}', orig[end+3:])
                new += docstr
                if smat:
                    new += orig[end:smat.span()[1]+ end + 3]
                else:
                    new += orig[end:]

        open("conv\\"+file, "w").write(new)






