import io;
import MolDisplay;
from http.server import HTTPServer, BaseHTTPRequestHandler;

class MyHandler( BaseHTTPRequestHandler ):
    def do_GET(self):
        if self.path == "/":
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", len(home_page) );
            self.end_headers();

            self.wfile.write( bytes( home_page, "utf-8" ) );

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );

    
    
    def do_POST(self):
        if self.path == "/molecule":
            self.send_response( 200 );
            mol = MolDisplay.Molecule();
            skip = next(self.rfile);
            skip = next(self.rfile);
            skip = next(self.rfile);
            skip = next(self.rfile);
            file = io.StringIO(self.rfile.read(int(self.headers.get('content-length'))).decode('utf-8'));
            # content = file.readlines();
            # for i in range(10):
            #     print(content[i], end= "");
            mol.parse(file);
            string = mol.svg();
            # print(string);
            self.send_header( "Content-type", "image/svg+xml" );
            self.send_header( "Content-length", len(string) );
            self.end_headers();

            self.wfile.write( bytes( string, "utf-8" ) );

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );




home_page = """
<html>
  <head>
    <title> File Upload </title> 
  </head>
  <body>
    <h1> File Upload </h1>
  <form action="molecule" enctype="multipart/form-data" method="post"> 
   <p>
      <input type="file" id="sdf_file" name="filename"/> 
   </p>
      <p>
        <input type="submit" value="Upload"/>
      </p> 
    </form>
  </body>
</html>
"""

#use port 57585
httpd = HTTPServer( ( 'localhost', 57585  ), MyHandler );
httpd.serve_forever();