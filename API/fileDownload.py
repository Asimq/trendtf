"""
@author: AsimA

Target: FastAPI based Async API for downloading files
 
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse

app = FastAPI()

#pdf
@app.get("/dtf/pdf/{file_name}")
async def download_file(file_name: str):
    file_path = f"/mnt/drive/Pdfs/MASTER/{file_name}.pdf"
    return FileResponse(file_path)

#rawtxt
@app.get("/dtf/rawtxt/{file_name}")
async def download_file(file_name: str):
    file_path = f"/mnt/drive/dtf_text/alltext/{file_name}.txt"
    return FileResponse(file_path)

#preprocessed
@app.get("/dtf/prepv1/{file_name}")
async def download_file(file_name: str):
    file_path = f"/mnt/drive/dtf_text/lemmatized/{file_name}.txt"
    return FileResponse(file_path)

#Metadata

#xml
@app.get("/dtf/metadata/xml/{file_name}")
async def download_file(file_name: str):
    file_path = f"/mnt/drive/metadata/ExtractedMetaDataXml/ExtractedMetaDataXml/{file_name}.xml"
    return FileResponse(file_path)

#json
@app.get("/dtf/metadata/json/{file_name}")
async def download_file(file_name: str):
    file_path = f"/mnt/drive/metadata/ExtractedMetaDataJson/ExtractedMetaDataJson/{file_name}.json"
    return FileResponse(file_path)

#json_dc
@app.get("/dtf/metadata/json_dc/{file_name}")
async def download_file(file_name: str):
    file_path = f"/mnt/drive/metadata/dc_json/{file_name}.json"
    return FileResponse(file_path)

#ftx
@app.get("/dtf/metadata/ftx/{file_name}")
async def download_file(file_name: str):
    file_path = f"/mnt/drive/metadata/ftx/{file_name}.xml"
    return FileResponse(file_path)


@app.get("/")
async def test_API():
    html_content = "<!DOCTYPE html>\
        <html>\
        <head>\
	        <title>API Services</title>\
        </head>\
        <body>\
	    <p>API IS WORKING!<br>\
         <ol> </ol>\
	    The API offers currently the following services:</p>\
	    <ol>\
		<li>Download PDF file of a DTF report using PPN at /dtf/pdf/'PPN' - Replace the string PPN with the actual PPN</li>\
		<li>Download extracted text from PDF for a DTF report using PPN at /dtf/rawtxt/'PPN' - Replace the string PPN with the actual PPN</li>\
        <li>Download preprocessed text of a DTF report using PPN at /dtf/prepv1/'PPN' - Replace the string PPN with the actual PPN</li>\
        <li>Download JSON metadata for a PPN at /dtf/metadata/json/'PPN' - Replace the string PPN with the actual PPN</li>\
        <li>Download XML metadata for a PPN at /dtf/metadata/xml/'PPN' - Replace the string PPN with the actual PPN</li>\
        <li>Download DC-JSON metadata for a PPN at /dtf/metadata/dc_json/'PPN' - Replace the string PPN with the actual PPN</li>\
        <li>Download FTX metadata for a PPN at /dtf/metadata/ftx/'PPN' - Replace the string PPN with the actual PPN</li>\
	</ol>\
    </body>\
    </html>\
"
    return HTMLResponse(content=html_content)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='trendtf23.osl.tib.eu', port=8123)
