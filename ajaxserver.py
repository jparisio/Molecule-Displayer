from http.server import HTTPServer, BaseHTTPRequestHandler;

import sys;     # to get command line argument for port
import urllib;  # code to parse for data
import io;
import molsql;
import MolDisplay;
import cgi;
import molecule;


# list of files that we allow the web-server to serve to clients
# (we don't want to serve any file that the client requests)
public_files = ['/style.css', '/script.js', '/select.html', '/upload.html'];
database = molsql.Database(reset = True);
database.create_tables();
database['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
database['Elements'] = ( 6, 'C', 'Carbon', '808080', '010101', '000000', 40 );
database['Elements'] = ( 7, 'N', 'Nitrogen', '0000FF', '000005', '000002', 40 );
database['Elements'] = ( 8, 'O', 'Oxygen', 'FF0000', '050000', '020000', 40 );

class MyHandler( BaseHTTPRequestHandler ):
    def do_GET(self):

        # used to GET a file from the list ov public_files, above
        if self.path in public_files:   # make sure it's a valid file
            self.send_response( 200 );  # OK
            self.send_header( "Content-type", "text/html" );

            fp = open( self.path[1:] ); 
            # [1:] to remove leading / so that file is found in current dir

            # load the specified file
            page = fp.read();
            fp.close();

            # create and send headers
            self.send_header( "Content-length", len(page) );
            self.end_headers();

            # send the contents
            self.wfile.write( bytes( page, "utf-8" ) );
        
        elif self.path == "/":   # make sure it's a valid file
            self.path += "index.html"
            self.send_response( 200 );  # OK
            self.send_header( "Content-type", "text/html" );

            fp = open( self.path[1:]); 
            # [1:] to remove leading / so that file is found in current dir

            # load the specified file
            page = fp.read();
            fp.close();

            # create and send headers
            self.send_header( "Content-length", len(page) );
            self.end_headers();

            # send the contents
            self.wfile.write( bytes( page, "utf-8" ) );

        else:
            # if the requested URL is not one of the public_files
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );



    def do_POST(self):

        if self.path == "/sdf_upload.html":
           
           #file upload

            cgi.parse_header(self.headers['Content-Type'])
            form = cgi.FieldStorage(
                fp = self.rfile,
                headers = self.headers,
                environ = {'REQUEST_METHOD': 'POST'}
            )

            # print(form);

            file_item = form['file']
            contents = file_item.file.read()
            molName = form.getvalue("molName").upper();

            bytes_io = io.BytesIO(contents)
            file = io.TextIOWrapper(bytes_io)
            # print(file)

            cursor = database.conn.cursor()

            included = database.checkItem2(str(molName.strip()));

            if(included == False):
                database.add_molecule(molName.strip(), file);
                message = "sdf file uploaded to database";
            else:
                message = "Molecule already exists, upload did not occur"

            # print(file);
            # print(contents)
            # print(molName)
            # cursor = database.conn.cursor()


            print(cursor.execute("SELECT * FROM Molecules").fetchall());

            # message = "sdf file uploaded to database";

            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );

        elif self.path == "/form_handler.html":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            print( repr( body.decode('utf-8') ) );

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );

            cursor = database.conn.cursor();
            elems = (cursor.execute("SELECT ELEMENT_CODE FROM Elements").fetchall());
            string = ""
            for i in range (len(elems)):
                if (i == len(elems) - 1):
                    string += str(elems[i][0]) + " "
                else:
                    string += str(elems[i][0]) + ", "

            print(string);
            
            

            print( postvars );
            # db['Elements'] = ( 1, 'H', 'Hydrogen', 'FFFFFF', '050505', '020202', 25 );
            if postvars['number'][0].isnumeric() and postvars['radius'][0].isnumeric() and (postvars['name'][0]).isnumeric() == False and (postvars['code'][0]).isnumeric() == False:
                if(database.checkItem(postvars['code'][0]) == False):
                  database['Elements'] = (str(postvars['number'][0]), str(postvars['code'][0]), str(postvars['name'][0]), str(postvars['c1'][0]), str(postvars['c2'][0]), str(postvars['c3'][0]), str(postvars['radius'][0]));
                  message = string + ", " + str(postvars['code'][0]);
                else:
                    message = "element code already exists";
            else:
                message = "incorrect values entered";



            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );
        
        elif self.path == "/deleteElement.html":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            print( repr( body.decode('utf-8') ) );

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );

            print( postvars );
            if(postvars['eNumber'][0].isnumeric()):
                message = "you must enter a valid element code, ex: H"
            elif len(postvars['eNumber'][0]) > 3:
                message = "you must enter a valid element code, ex: H"
            else:
                database.deleteItem(str(postvars['eNumber'][0]));
                cursor = database.conn.cursor();
                elems = (cursor.execute("SELECT ELEMENT_CODE FROM Elements").fetchall());
                string = ""
                for i in range (len(elems)):
                    if (i == len(elems) - 1):
                        string += str(elems[i][0]) + " "
                    else:
                        string += str(elems[i][0]) + ", "
                        
                message = string;

            dict = database.element_name();
            print(dict);

            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );
        

        elif self.path == "/moleculesList.html":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            print( repr( body.decode('utf-8') ) );

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );

            # print( postvars );

            cursor = database.conn.cursor()

            mols = (cursor.execute("SELECT NAME FROM Molecules").fetchall());
            string = ''
            for i in range (len(mols)):
                mol = database.load_mol(mols[i][0]);
                atoms = str(mol.atom_no)
                bonds = str(mol.bond_no)
                string += str(mols[i][0]).upper() + ' atoms:' + atoms + ' bonds:' + bonds + ' ';
            print(string)
              
            
            message = string

            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );
        
        elif self.path == "/display_sdf.html":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            print( repr( body.decode('utf-8') ) );

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );
            mol_name = postvars['mol'][0].upper();
            print(mol_name);

            cursor = database.conn.cursor();

            included = database.checkItem2(str(mol_name.strip()));

            if(included == True):   
                MolDisplay.radius = database.radius();
                MolDisplay.element_name = database.element_name();
                MolDisplay.header += database.radial_gradients();
                mol = database.load_mol(mol_name);
                string = mol.svg();
                # mol.sort();
                print(string);
                # cursor = database.conn.cursor()

                # mols = (cursor.execute("SELECT NAME FROM Molecules").fetchall());
                message = string
            else:
                message = "Molecule doesnt exist"


            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );


        elif self.path == "/rotate.html":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            print( repr( body.decode('utf-8') ) );

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );
            print(postvars);
            rotatedImage = postvars['svg_image'][0];
            print(postvars['r1'][0])
            print(postvars['r2'][0])
            print(postvars['r3'][0])
            if postvars['r1'][0].isnumeric() == False or postvars['r2'][0].isnumeric() == False or postvars['r3'][0].isnumeric() == False:
                message = "incorrect values input"
            elif ((int(postvars['r3'][0]) == 0 and int(postvars['r2'][0]) == 0) or (int(postvars['r1'][0]) == 0 and int(postvars['r2'][0]) == 0) or (int(postvars['r3'][0]) == 0 and int(postvars['r1'][0]) == 0)):
                print("in func")
                r1 = int(postvars['r1'][0]);
                r2 = int(postvars['r2'][0]);
                r3 = int(postvars['r3'][0]);

                print( r1, r2, r3);
                
                print(rotatedImage);
                mol = database.load_mol(rotatedImage.upper());
                mx = molecule.mx_wrapper(r1, r2, r3);
                mol.xform( mx.xform_matrix );
                string = mol.svg();
                message = string
            else:
                message = "incorrect values input"
                

            # message = "nice"



            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );
        
        elif self.path == "/reload_page.html":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            print( repr( body.decode('utf-8') ) );

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );

            cursor = database.conn.cursor();
            elems = (cursor.execute("SELECT ELEMENT_CODE FROM Elements").fetchall());
            string = ""
            for i in range (len(elems)):
                if (i == len(elems) - 1):
                    string += str(elems[i][0]) + " "
                else:
                    string += str(elems[i][0]) + ", "

            print(string)

            message = string;

            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );




httpd = HTTPServer( ( 'localhost', 57585  ), MyHandler );
httpd.serve_forever();
