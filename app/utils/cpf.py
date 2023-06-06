from app.extensions.database import get_db


def cpf_validate(cpf):
    cpf = "".join(filter(str.isdigit, cpf))  # Remove non-digit characters
    if len(cpf) != 11 or not cpf.isdigit():
        return False

    # Validate the CPF digits
    cpf_digits = [int(digit) for digit in cpf]
    if len(set(cpf_digits)) == 1:  # Check if all digits are the same
        return False

    # Calculate the first verification digit
    sum_1 = sum(digit * weight for digit, weight in zip(cpf_digits[:9], range(10, 1, -1)))
    digit_1 = (sum_1 * 10) % 11
    if digit_1 == 10:
        digit_1 = 0

    # Calculate the second verification digit
    sum_2 = sum(digit * weight for digit, weight in zip(cpf_digits[:10], range(11, 1, -1)))
    digit_2 = (sum_2 * 10) % 11
    if digit_2 == 10:
        digit_2 = 0

    # Check if the verification digits match
    return digit_1 == cpf_digits[9] and digit_2 == cpf_digits[10]


def cpf_search(cpf):
    con = get_db()
    with con.cursor() as cur:
        cur.execute('SELECT cpf FROM coloquios.pessoa WHERE cpf = %s;', (cpf,))
        con.commit()
        data_raw = cur.fetchone()
        return data_raw is not None


def cpf_search_palestrante(cpf, id):
    con = get_db()
    with con.cursor() as cur:
        cur.execute(
            'SELECT cpf FROM coloquios.pessoa pessoa '
            'JOIN coloquios.palestrante palestrante ON pessoa.id = palestrante.idpal '
            'WHERE pessoa.cpf = %s and palestrante.idcol = %s;',
            (cpf, id)
        )
        con.commit()
        data_raw = cur.fetchone()
        return data_raw is not None
