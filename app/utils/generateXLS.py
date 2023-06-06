from io import BytesIO

import xlsxwriter
from flask import make_response


def generate(id):
    from app.extensions.database import get_db
    con = get_db()
    with con.cursor() as cur:
        output = BytesIO()

        cur.execute(
            'SELECT nome, curso, cpf, datanasc  FROM coloquios.pessoa pessoa JOIN '
            'coloquios.participante ba ON pessoa.id = ba.idpar JOIN coloquios.apresentacao b ON b.id = ba.idcol '
            'WHERE b.id = %s '
            'ORDER BY nome;',
            (id,))
        rows = cur.fetchall()
        cur.execute('select * from coloquios.apresentacao where id = %s', (id,))
        col = cur.fetchone()
        con.commit()

        # Create a new Excel file and add a worksheet
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Define cell formats
        formatOne = workbook.add_format()
        formatOne.set_font_name('Cambria')
        formatTwo = workbook.add_format()
        formatTwo.set_font_name('Calibri')
        red_bold_italic = workbook.add_format({'bold': True, 'italic': True, 'bg_color': '#FF0000'})
        bold_italic = workbook.add_format({'bold': True, 'italic': True})
        border_format = workbook.add_format({
            'left': 1,
            'right': 1
            , 'bold': True, 'italic': True})
        # Write headers
        a = ['Nome', 'Data Nasc.', 'Tipo Doc.', 'Número do Documento', 'Endereço', 'Email', 'Nome da mãe',
             'Tipo de Participação', 'CH', 'Extra 1', 'Extra 2', 'Extra 3']
        worksheet.write('A1', a[0], red_bold_italic)
        worksheet.write('B1', a[1], red_bold_italic)
        worksheet.write('C1', a[2], bold_italic)
        worksheet.write('D1', a[3], red_bold_italic)
        worksheet.write('E1', a[4], bold_italic)
        worksheet.write('F1', a[5], bold_italic)
        worksheet.write('G1', a[6], bold_italic)
        worksheet.write('H1', a[7], red_bold_italic)
        worksheet.write('I1', a[8], red_bold_italic)
        worksheet.write('J1', a[9], bold_italic)
        worksheet.write('K1', a[10], border_format)
        worksheet.write('L1', a[11], border_format)

        text_format = workbook.add_format({'num_format': '@'})
        worksheet.set_column('A:K', None, text_format)

        # Write data
        for i, row in enumerate(rows):
            row_num = i + 1
            formatted_date = row[3].strftime("%d/%m/%Y")
            cpf = row[2].replace('-', '')
            cpf = cpf.replace('.', '')
            worksheet.write(row_num, 0, row[0], formatOne)
            worksheet.write(row_num, 1, formatted_date, formatOne)
            worksheet.write(row_num, 2, 'CPF', formatOne)
            worksheet.write(row_num, 3, cpf, formatOne)
            worksheet.write(row_num, 7, 'Participante', formatTwo)
            worksheet.write(row_num, 8, '1', formatTwo)

        # Set column widths
        worksheet.set_column(0, 0, 5)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 25)
        worksheet.set_column(3, 3, 25)
        worksheet.set_column(4, 4, 25)

        # Close the workbook
        workbook.close()

        output.seek(0)

        # Send the file as a response to the client
        filename = col[1] + '.xlsx'
        response = make_response(output.read())

        # Set the headers to force browser to download the file
        response.headers.set('Content-Type', 'application/vnd.ms-excel')
        response.headers.set('Content-Disposition', 'attachment', filename=filename)
    return response
