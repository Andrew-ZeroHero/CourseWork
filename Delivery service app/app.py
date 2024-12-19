from initial import *
from models import User, Delivery, DeliveryLog

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login, password=password).first()

        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'manager':
                return redirect(url_for('manager_dashboard'))
            elif user.role == 'courier':
                return redirect(url_for('courier_dashboard'))
            else:
                return render_template('outsider_dashboard.html')
        else:
            flash('Неверный логин или пароль', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
        login = request.form['login']
        password = request.form['password']

        new_user = User(full_name=full_name, phone_number=phone_number, birth_date=birth_date, login=login, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрированы', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/manager_dashboard')
def manager_dashboard():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))
    deliveries = Delivery.query.order_by(Delivery.status.desc(), Delivery.id.asc()).all()
    return render_template('manager_dashboard.html', deliveries=deliveries)

@app.route('/courier_dashboard')
def courier_dashboard():
    if 'user_id' not in session or session['role'] != 'courier':
        return redirect(url_for('login'))
    courier_id = session['user_id']
    active_deliveries = Delivery.query.filter_by(status='in_process').all()
    available_deliveries = Delivery.query.filter_by(status='waiting').all()
    return render_template('courier_dashboard.html', active_deliveries=active_deliveries, available_deliveries=available_deliveries)

@app.route('/manager/deliveries', methods=['GET'])
def deliveries():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    deliveries_list = Delivery.query.order_by(
        Delivery.status.desc(), Delivery.delivery_number.asc()
    ).all()  # Сортировка по статусу и номеру

    return render_template('deliveries.html', deliveries=deliveries_list)

@app.route('/delivery_details/<int:id>', methods=['GET', 'POST'])
def delivery_details(id):
    delivery = Delivery.query.get_or_404(id)
    if request.method == 'POST':
        if 'start_delivery' in request.form:
            # Система начала доставки
            if delivery.status == 'waiting':
                delivery.status = 'in_process'
                db.session.commit()
                flash('Доставка начата', 'success')
            return redirect(url_for('courier_dashboard'))
        elif 'confirm_delivery' in request.form:
            # Система подтверждения доставки
            code = request.form['code']
            if code == str(random.randint(1000, 9999)):  # Пример кода
                delivery.status = 'delivered'
                db.session.commit()
                flash('Доставка подтверждена', 'success')
                return redirect(url_for('courier_dashboard'))
    return render_template('delivery_details.html', delivery=delivery)

@app.route('/delivery_log')
def delivery_log():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))
    logs = DeliveryLog.query.all()
    return render_template('delivery_log.html', logs=logs)


@app.route('/manager/add_delivery', methods=['GET', 'POST'])
def add_delivery():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Получение данных из формы
        delivery_address = request.form['address']
        customer_phone = request.form['customer_phone']
        order_number = request.form['order_number']
        order_content = request.form['order_content']

        # Логика добавления новой доставки
        new_delivery = Delivery(
            address=delivery_address,
            customer_phone=customer_phone,
            order_number=order_number,
            order_content=order_content,
            status='waiting'
        )
        db.session.add(new_delivery)
        db.session.commit()
        flash('Доставка успешно добавлена!', 'success')
        return redirect(url_for('manager_dashboard'))

    return render_template('add_delivery.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/manager/couriers', methods=['GET'])
def couriers():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    couriers_list = User.query.filter_by(role='courier').all()  # Получение списка курьеров из базы данных
    return render_template('couriers.html', couriers=couriers_list)


@app.route('/manager/edit_courier/<int:courier_id>', methods=['GET', 'POST'])
def edit_courier(courier_id):
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    courier = User.query.get_or_404(courier_id)

    if request.method == 'POST':
        # Обновление информации о курьере
        courier.full_name = request.form['full_name']
        courier.phone_number = request.form['phone_number']
        courier.birth_date = request.form['birth_date']
        courier.login = request.form['login']

        db.session.commit()
        flash('Информация о курьере обновлена!', 'success')
        return redirect(url_for('couriers'))

    if request.method == 'DELETE':  # Обработка удаления
        db.session.delete(courier)
        db.session.commit()
        flash('Курьер удален!', 'success')
        return redirect(url_for('couriers'))

    return render_template('edit_courier.html', courier=courier)


@app.route('/manager/outsiders', methods=['GET'])
def outsiders():
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    outsiders_list = User.query.filter_by(role='outsider').all()  # Получение списка посторонних из базы данных
    return render_template('outsiders.html', outsiders=outsiders_list)


@app.route('/manager/edit_outsider/<int:outsider_id>', methods=['GET', 'POST', 'DELETE'])
def edit_outsider(outsider_id):
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    outsider = User.query.get_or_404(outsider_id)

    if request.method == 'POST':
        if 'promote' in request.form:  # Повышение до курьера
            if outsider and outsider.role == 'outsider':
                outsider.role = 'courier'
                db.session.commit()
            flash('Пользователь повышен до роли курьера!', 'success')
            return redirect(url_for('outsiders'))

        elif 'delete' in request.form:  # Удаление постороннего
            db.session.delete(outsider)
            db.session.commit()
            flash('Посторонний удален!', 'success')
            return redirect(url_for('outsiders'))

    return render_template('edit_outsider.html', outsider=outsider)

@app.route('/manager/edit_delivery/<int:delivery_id>', methods=['GET', 'POST', 'DELETE'])
def edit_delivery(delivery_id):
    if 'user_id' not in session or session['role'] != 'manager':
        return redirect(url_for('login'))

    delivery = Delivery.query.get_or_404(delivery_id)

    if request.method == 'POST':
        # Обновление данных доставки
        delivery.address = request.form['address']
        delivery.phone_number = request.form['phone_number']
        delivery.order_ids = request.form['order_ids']
        delivery.contents = request.form['contents']
        delivery.status = request.form['status']

        db.session.commit()
        flash('Информация о доставке обновлена!', 'success')
        return redirect(url_for('deliveries'))

    if request.method == 'DELETE':  # Удаление доставки
        db.session.delete(delivery)
        db.session.commit()
        flash('Доставка удалена!', 'success')
        return redirect(url_for('deliveries'))

    return render_template('edit_delivery.html', delivery=delivery)



@app.before_request
def handle_delete_method():
    if request.method == 'POST' and '_method' in request.form:
        if request.form['_method'].upper() == 'DELETE':
            request.environ['REQUEST_METHOD'] = 'DELETE'


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
