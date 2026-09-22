from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import mysql.connector
import os
from functools import wraps

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    'SECRET_KEY',
    'ctech-dev-secret-key'
)

UPLOAD_FOLDER = os.path.join(
    'static',
    'uploads'
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    'png',
    'jpg',
    'jpeg',
    'webp'
}


DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'ctech')
}


def get_db():

    return mysql.connector.connect(
        **DB_CONFIG
    )


def query(
    sql,
    params=(),
    fetch=False
):

    conn = get_db()

    cursor = conn.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            sql,
            params
        )

        if fetch:

            return cursor.fetchall()

        conn.commit()

        return cursor.lastrowid

    finally:

        cursor.close()

        conn.close()


def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if 'user_id' not in session:

            return redirect(
                url_for('login')
            )

        return function(
            *args,
            **kwargs
        )

    return wrapper


def allowed_file(filename):

    return (
        '.' in filename
        and
        filename.rsplit(
            '.',
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route('/')
def splash():

    return render_template(
        'splash.html'
    )


@app.route(
    '/login',
    methods=['GET', 'POST']
)
def login():

    if request.method == 'POST':

        login_value = request.form.get(
            'login',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        cpf_login = ''.join(
            filter(
                str.isdigit,
                login_value
            )
        )

        if len(cpf_login) == 11:

            login_value = cpf_login

        user = query(
            '''
            SELECT *
            FROM users
            WHERE cpf=%s
               OR email=%s
            LIMIT 1
            ''',
            (
                login_value,
                login_value
            ),
            True
        )

        if user:

            current_user = user[0]

            if check_password_hash(
                current_user['password_hash'],
                password
            ):

                session['user_id'] = current_user['id']

                session['user_name'] = current_user['name']

                return redirect(
                    url_for('dashboard')
                )

        flash(
            'CPF/e-mail ou senha inválidos.'
        )

    return render_template(
        'login.html'
    )


@app.route(
    '/cadastro',
    methods=['GET', 'POST']
)
def cadastro():

    if request.method == 'POST':

        name = request.form.get(
            'name',
            ''
        ).strip()

        cpf = request.form.get(
            'cpf',
            ''
        ).strip()

        email = request.form.get(
            'email',
            ''
        ).strip()

        role = request.form.get(
            'role',
            'Colaborador'
        ).strip()

        password = request.form.get(
            'password',
            ''
        )

        password_confirm = request.form.get(
            'password_confirm',
            ''
        )

        cpf = ''.join(
            filter(
                str.isdigit,
                cpf
            )
        )

        if not name or not cpf or not email or not password:

            flash(
                'Preencha todos os campos obrigatórios.'
            )

            return render_template(
                'cadastro.html'
            )

        if len(cpf) != 11:

            flash(
                'O CPF deve conter exatamente 11 dígitos.'
            )

            return render_template(
                'cadastro.html'
            )

        if len(password) < 6:

            flash(
                'A senha deve ter pelo menos 6 caracteres.'
            )

            return render_template(
                'cadastro.html'
            )

        if password != password_confirm:

            flash(
                'As senhas não coincidem.'
            )

            return render_template(
                'cadastro.html'
            )

        existing_user = query(
            '''
            SELECT id
            FROM users
            WHERE cpf=%s
               OR email=%s
            LIMIT 1
            ''',
            (
                cpf,
                email
            ),
            True
        )

        if existing_user:

            flash(
                'CPF ou e-mail já cadastrado.'
            )

            return render_template(
                'cadastro.html'
            )

        password_hash = generate_password_hash(
            password
        )

        try:

            query(
                '''
                INSERT INTO users
                (
                    name,
                    cpf,
                    email,
                    role,
                    password_hash
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                ''',
                (
                    name,
                    cpf,
                    email,
                    role,
                    password_hash
                )
            )

            flash(
                'Cadastro realizado com sucesso! Faça login.'
            )

            return redirect(
                url_for('login')
            )

        except mysql.connector.Error:

            flash(
                'Não foi possível realizar o cadastro.'
            )

    return render_template(
        'cadastro.html'
    )


@app.route('/dashboard')
@login_required
def dashboard():

    products = query(
        '''
        SELECT *
        FROM products
        ORDER BY id DESC
        ''',
        fetch=True
    )

    orders = query(
        '''
        SELECT *
        FROM orders
        ORDER BY id DESC
        LIMIT 5
        ''',
        fetch=True
    )

    return render_template(
        'dashboard.html',
        products=products,
        orders=orders
    )


@app.route(
    '/produto/novo',
    methods=['GET', 'POST']
)
@login_required
def novo_produto():

    if request.method == 'POST':

        name = request.form.get(
            'name',
            ''
        ).strip()

        product_code = request.form.get(
            'product_id',
            ''
        ).strip()

        try:

            quantity = int(
                request.form.get(
                    'quantity'
                ) or 0
            )

        except ValueError:

            quantity = 0

        image = request.files.get(
            'image'
        )

        image_name = None

        if (
            image
            and
            image.filename
            and
            allowed_file(image.filename)
        ):

            image_name = secure_filename(
                image.filename
            )

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    image_name
                )
            )

        if not name or not product_code:

            flash(
                'Nome e código do produto são obrigatórios.'
            )

            return render_template(
                'novo_produto.html'
            )

        if quantity < 0:

            quantity = 0

        try:

            query(
                '''
                INSERT INTO products
                (
                    name,
                    product_code,
                    quantity,
                    image
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                ''',
                (
                    name,
                    product_code,
                    quantity,
                    image_name
                )
            )

            flash(
                'Produto cadastrado com sucesso!'
            )

            return redirect(
                url_for('dashboard')
            )

        except mysql.connector.Error:

            flash(
                'Código do produto já existe.'
            )

    return render_template(
        'novo_produto.html'
    )


@app.route(
    '/produto/<int:product_id>/atualizar',
    methods=['GET', 'POST']
)
@login_required
def atualizar_produto(product_id):

    product = query(
        '''
        SELECT *
        FROM products
        WHERE id=%s
        ''',
        (product_id,),
        True
    )

    if not product:

        flash(
            'Produto não encontrado.'
        )

        return redirect(
            url_for('dashboard')
        )

    product = product[0]

    if request.method == 'POST':

        try:

            quantity = int(
                request.form.get(
                    'quantity'
                ) or 0
            )

        except ValueError:

            quantity = 0

        if quantity < 0:

            quantity = 0

        image = request.files.get(
            'image'
        )

        image_name = product.get(
            'image'
        )

        if (
            image
            and
            image.filename
            and
            allowed_file(image.filename)
        ):

            image_name = secure_filename(
                image.filename
            )

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    image_name
                )
            )

        query(
            '''
            UPDATE products
            SET
                quantity=%s,
                image=%s,
                updated_at=NOW()
            WHERE id=%s
            ''',
            (
                quantity,
                image_name,
                product_id
            )
        )

        flash(
            'Produto atualizado com sucesso!'
        )

        return redirect(
            url_for('dashboard')
        )

    return render_template(
        'atualizar_produto.html',
        product=product
    )


@app.post(
    '/produto/<int:product_id>/excluir'
)
@login_required
def excluir_produto(product_id):

    product = query(
        '''
        SELECT *
        FROM products
        WHERE id=%s
        ''',
        (product_id,),
        True
    )

    if not product:

        flash(
            'Produto não encontrado.'
        )

        return redirect(
            url_for('dashboard')
        )

    try:

        query(
            '''
            DELETE FROM products
            WHERE id=%s
            ''',
            (product_id,)
        )

        flash(
            'Produto excluído com sucesso!'
        )

    except mysql.connector.Error:

        flash(
            'Não foi possível excluir o produto. Ele pode estar vinculado a um pedido.'
        )

    return redirect(
        url_for('dashboard')
    )


@app.route(
    '/pedido/novo',
    methods=['GET', 'POST']
)
@login_required
def novo_pedido():

    products = query(
        '''
        SELECT *
        FROM products
        ORDER BY name
        ''',
        fetch=True
    )

    if request.method == 'POST':

        client = request.form.get(
            'client',
            ''
        ).strip()

        project = request.form.get(
            'project',
            ''
        ).strip()

        machine = request.form.get(
            'machine',
            ''
        ).strip()

        if not client or not project or not machine:

            flash(
                'Preencha todos os campos do pedido.'
            )

            return render_template(
                'novo_pedido.html',
                products=products
            )

        selected_products = []

        for product in products:

            try:

                quantity = int(
                    request.form.get(
                        f"quantity_{product['id']}"
                    ) or 0
                )

            except ValueError:

                quantity = 0

            if quantity < 0:

                quantity = 0

            if quantity > product['quantity']:

                flash(
                    f"Estoque insuficiente para {product['name']}."
                )

                return render_template(
                    'novo_pedido.html',
                    products=products
                )

            if quantity > 0:

                selected_products.append(
                    (
                        product['id'],
                        quantity
                    )
                )

        if not selected_products:

            flash(
                'Selecione pelo menos um produto.'
            )

            return render_template(
                'novo_pedido.html',
                products=products
            )

        try:

            order_id = query(
                '''
                INSERT INTO orders
                (
                    client,
                    project,
                    machine
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
                ''',
                (
                    client,
                    project,
                    machine
                )
            )

            for product_id, quantity in selected_products:

                query(
                    '''
                    INSERT INTO order_items
                    (
                        order_id,
                        product_id,
                        quantity
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s
                    )
                    ''',
                    (
                        order_id,
                        product_id,
                        quantity
                    )
                )

                query(
                    '''
                    UPDATE products
                    SET quantity = quantity - %s
                    WHERE id=%s
                    ''',
                    (
                        quantity,
                        product_id
                    )
                )

            flash(
                'Pedido criado com sucesso!'
            )

            return redirect(
                url_for('pedidos')
            )

        except mysql.connector.Error:

            flash(
                'Não foi possível criar o pedido.'
            )

    return render_template(
        'novo_pedido.html',
        products=products
    )


@app.route('/pedidos')
@login_required
def pedidos():

    orders = query(
        '''
        SELECT *
        FROM orders
        ORDER BY id DESC
        ''',
        fetch=True
    )

    return render_template(
        'pedidos.html',
        orders=orders
    )


@app.route(
    '/pedido/<int:order_id>'
)
@login_required
def detalhe_pedido(order_id):

    order = query(
        '''
        SELECT *
        FROM orders
        WHERE id=%s
        ''',
        (order_id,),
        True
    )

    if not order:

        flash(
            'Pedido não encontrado.'
        )

        return redirect(
            url_for('pedidos')
        )

    items = query(
        '''
        SELECT
            oi.*,
            p.name,
            p.product_code
        FROM order_items oi
        JOIN products p
            ON p.id = oi.product_id
        WHERE oi.order_id=%s
        ''',
        (order_id,),
        True
    )

    return render_template(
        'detalhe_pedido.html',
        order=order[0],
        items=items
    )


@app.post(
    '/pedido/<int:order_id>/excluir'
)
@login_required
def excluir_pedido(order_id):

    order = query(
        '''
        SELECT *
        FROM orders
        WHERE id=%s
        ''',
        (order_id,),
        True
    )

    if not order:

        flash(
            'Pedido não encontrado.'
        )

        return redirect(
            url_for('pedidos')
        )

    items = query(
        '''
        SELECT
            product_id,
            quantity
        FROM order_items
        WHERE order_id=%s
        ''',
        (order_id,),
        True
    )

    try:

        for item in items:

            query(
                '''
                UPDATE products
                SET quantity = quantity + %s
                WHERE id=%s
                ''',
                (
                    item['quantity'],
                    item['product_id']
                )
            )

        query(
            '''
            DELETE FROM orders
            WHERE id=%s
            ''',
            (order_id,)
        )

        flash(
            'Pedido excluído e estoque restaurado com sucesso!'
        )

    except mysql.connector.Error:

        flash(
            'Não foi possível excluir o pedido.'
        )

    return redirect(
        url_for('pedidos')
    )


@app.post(
    '/api/pedido/<int:order_id>/status'
)
@login_required
def atualizar_status(order_id):

    data = request.get_json(
        silent=True
    ) or {}

    status = data.get(
        'status',
        ''
    )

    if status not in (
        'EM ANDAMENTO',
        'FINALIZADO'
    ):

        return jsonify(
            ok=False,
            message='Status inválido'
        ), 400

    query(
        '''
        UPDATE orders
        SET status=%s
        WHERE id=%s
        ''',
        (
            status,
            order_id
        )
    )

    return jsonify(
        ok=True,
        status=status
    )


@app.get('/api/produtos')
@login_required
def api_produtos():

    products = query(
        '''
        SELECT *
        FROM products
        ORDER BY id DESC
        ''',
        fetch=True
    )

    return jsonify(
        products
    )


@app.get('/logout')
def logout():

    session.clear()

    return redirect(
        url_for('login')
    )


@app.errorhandler(
    mysql.connector.Error
)
def db_error(error):

    return (
        'Erro de conexão com o MySQL. '
        'Confira o arquivo .env e se o MySQL está ligado.',
        500
    )


if __name__ == '__main__':

    os.makedirs(
        app.config['UPLOAD_FOLDER'],
        exist_ok=True
    )

    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000
    )