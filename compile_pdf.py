import subprocess
import sys
import os
import urllib.request
import urllib.parse

def compile_local(tex_filename, pdf_filename):
    print(f"Compiling {tex_filename} locally using pdflatex...")
    try:
        # Run pdflatex compile command twice to ensure cross-references are resolved
        for i in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print("Local compilation failed with errors:")
                print(result.stdout)
                print(result.stderr)
                return False
        
        # Clean up auxiliary files
        aux_extensions = [".aux", ".log", ".out", ".toc"]
        for ext in aux_extensions:
            aux_file = tex_filename.replace(".tex", ext)
            if os.path.exists(aux_file):
                os.remove(aux_file)
                
        print(f"Successfully compiled locally! Output file is {pdf_filename}")
        return True
    except FileNotFoundError:
        return False

def compile_online(tex_filename, pdf_filename):
    print("Local pdflatex compile engine not found.")
    print(f"Attempting to compile {tex_filename} online using the free texlive.net API...")
    
    try:
        with open(tex_filename, 'r', encoding='utf-8') as f:
            latex_content = f.read()
            
        url = "https://texlive.net/cgi-bin/latexcgi"
        
        import uuid
        boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
        
        fields = [
            ('filename[]', 'document.tex'),
            ('filecontents[]', latex_content),
            ('engine', 'pdflatex'),
            ('return', 'pdf')
        ]
        
        body = []
        for key, value in fields:
            body.append(f'--{boundary}')
            body.append(f'Content-Disposition: form-data; name="{key}"')
            body.append('')
            body.append(value)
        body.append(f'--{boundary}--')
        body.append('')
        
        payload = '\r\n'.join(body).encode('utf-8')
        
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(payload))
        }
        
        req = urllib.request.Request(url, data=payload, headers=headers)
        
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status == 200:
                with open(pdf_filename, 'wb') as out_f:
                    out_f.write(response.read())
                print(f"Successfully compiled online! Output file is {pdf_filename}")
                return True
            else:
                print(f"Online compilation failed with status: {response.status}")
                return False
    except Exception as e:
        print(f"Error during online compilation: {e}")
        return False

def compile_file(tex_filename):
    pdf_filename = tex_filename.replace(".tex", ".pdf")
    
    # Try local compile first
    success = compile_local(tex_filename, pdf_filename)
    if not success:
        # Fall back to online compile
        success = compile_online(tex_filename, pdf_filename)
        
    return success

def compile_all():
    files = [
        "request_letter.tex",
        "recommendation_innovation_hub.tex",
        "recommendation_hod.tex",
        "undertaking_form.tex"
    ]
    failed = []
    
    for f in files:
        if not os.path.exists(f):
            print(f"Error: {f} not found.")
            failed.append(f)
            continue
            
        print("-" * 50)
        success = compile_file(f)
        if not success:
            failed.append(f)
            
    print("-" * 50)
    if failed:
        print(f"Compilation failed for: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("All documents compiled successfully!")

if __name__ == "__main__":
    compile_all()
