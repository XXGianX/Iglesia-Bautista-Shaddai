from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy import create_engine, Column, String, Integer, Float, Enum as SQLAlchemyEnum
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm.exc import NoResultFound
import enum
import uuid
from datetime import datetime

# Configuración
app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

Base = declarative_base()

# Enums para las opciones
class CategoriaItem(enum.Enum):
    MUEBLE = "Mueble"
    ELECTRONICO = "Electrónico"
    MATERIAL = "Material de oficina"
    HERRAMIENTA = "Herramienta"
    OTROS = "Otros"

class EstadoItem(enum.Enum):
    DISPONIBLE = "Disponible"
    EN_USO = "En uso"
    REPARACION = "En reparación"
    DESCARTADO = "Descartado"

class TipoCompra(enum.Enum):
    DONADO = "Donado"
    COMPRADO = "Comprado"

# Modelo de datos
class Item(Base):
    __tablename__ = 'items'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    cantidad = Column(Integer, default=1)
    valor_unitario = Column(Float)
    fecha_registro = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    categoria = Column(SQLAlchemyEnum(CategoriaItem), nullable=False)
    ubicacion = Column(String)
    estado = Column(SQLAlchemyEnum(EstadoItem), default=EstadoItem.DISPONIBLE)
    responsable = Column(String)
    tipo_compra = Column(SQLAlchemyEnum(TipoCompra), nullable=False)

# Base de datos SQLite
engine = create_engine('postgresql://inventario_db_wfvw_user:smimBiWfAvcXNckdabcl3omz5ceorVla@dpg-d190a27diees73acia6g-a.ohio-postgres.render.com/inventario_db_wfvw')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Página de inicio con login
@app.route('/', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        clave = request.form.get('clave')

        if usuario == 'crisologo' and clave == '123456':
            session['usuario'] = usuario
            return redirect(url_for('inventario'))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    return render_template('index.html')

# Sistema de inventario
@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    if 'usuario' not in session:
        return redirect(url_for('inicio'))

    session_db = Session()
    if request.method == 'POST':
        try:
            nuevo_item = Item(
                nombre=request.form['nombre'],
                descripcion=request.form.get('descripcion', ''),
                cantidad=int(request.form.get('cantidad', 1)),
                valor_unitario=float(request.form.get('valor_unitario', 0)),
                categoria=CategoriaItem(request.form['categoria']),
                ubicacion=request.form.get('ubicacion', ''),
                estado=EstadoItem(request.form.get('estado', EstadoItem.DISPONIBLE.value)),
                responsable=request.form.get('responsable', ''),
                tipo_compra=TipoCompra(request.form.get('tipo_compra', TipoCompra.COMPRADO.value))
            )
            session_db.add(nuevo_item)
            session_db.commit()
            flash("Ítem agregado con éxito", "success")
        except Exception as e:
            session_db.rollback()
            flash(f"Error al agregar: {e}", "error")
        finally:
            session_db.close()
        return redirect(url_for('inventario'))

    items = session_db.query(Item).order_by(Item.nombre).all()
    session_db.close()
    return render_template('inventario.html', items=items, categorias=CategoriaItem, estados=EstadoItem, tipos_compra=TipoCompra)

# Editar ítems
@app.route('/editar/<item_id>', methods=['GET', 'POST'])
def editar(item_id):
    if 'usuario' not in session:
        return redirect(url_for('inicio'))

    session_db = Session()
    item = session_db.query(Item).filter_by(id=item_id).first()
    if not item:
        session_db.close()
        flash("Ítem no encontrado", "error")
        return redirect(url_for('inventario'))

    if request.method == 'POST':
        try:
            item.nombre = request.form['nombre']
            item.descripcion = request.form.get('descripcion', '')
            item.cantidad = int(request.form.get('cantidad', 1))
            item.valor_unitario = float(request.form.get('valor_unitario', 0))
            item.categoria = CategoriaItem(request.form['categoria'])
            item.ubicacion = request.form.get('ubicacion', '')
            item.estado = EstadoItem(request.form.get('estado', EstadoItem.DISPONIBLE.value))
            item.responsable = request.form.get('responsable', '')
            item.tipo_compra = TipoCompra(request.form.get('tipo_compra', TipoCompra.COMPRADO.value))
            session_db.commit()
            flash("Ítem actualizado correctamente", "success")
        except Exception as e:
            session_db.rollback()
            flash(f"Error al actualizar ítem: {e}", "error")
        finally:
            session_db.close()
        return redirect(url_for('inventario'))

    session_db.close()
    return render_template('editar.html', item=item, categorias=CategoriaItem, estados=EstadoItem, tipos_compra=TipoCompra)

# Eliminar ítems
@app.route('/eliminar/<item_id>', methods=['POST'])
def eliminar(item_id):
    if 'usuario' not in session:
        return redirect(url_for('inicio'))

    session_db = Session()
    try:
        item = session_db.query(Item).filter_by(id=item_id).first()
        if item:
            session_db.delete(item)
            session_db.commit()
            flash("Ítem eliminado correctamente", "success")
        else:
            flash("Ítem no encontrado", "error")
    except Exception as e:
        session_db.rollback()
        flash(f"Error al eliminar ítem: {e}", "error")
    finally:
        session_db.close()
    return redirect(url_for('inventario'))

# Página de estadísticas
@app.route('/estadisticas')
def estadisticas():
    if 'usuario' not in session:
        return redirect(url_for('inicio'))
    return render_template('estadisticas.html')

# API de estadísticas para gráficos
@app.route('/api/estadisticas')
def api_estadisticas():
    if 'usuario' not in session:
        return jsonify({"error": "No autorizado"}), 401

    session_db = Session()
    try:
        data = {
            'categorias_nombres': [],
            'categorias_valores': [],
            'categorias_cantidades_items': [],
            'estados_nombres': [],
            'estados_valores': [],
            'estados_cantidades_items': [],
            'tipos_compra_nombres': [],
            'tipos_compra_valores': [],
            'tipos_compra_cantidades_items': []
        }

        for cat in CategoriaItem:
            items = session_db.query(Item).filter_by(categoria=cat).all()
            data['categorias_nombres'].append(cat.value)
            data['categorias_valores'].append(sum(i.valor_unitario * i.cantidad for i in items if i.valor_unitario))
            data['categorias_cantidades_items'].append(sum(i.cantidad for i in items))

        for est in EstadoItem:
            items = session_db.query(Item).filter_by(estado=est).all()
            data['estados_nombres'].append(est.value)
            data['estados_valores'].append(sum(i.valor_unitario * i.cantidad for i in items if i.valor_unitario))
            data['estados_cantidades_items'].append(sum(i.cantidad for i in items))

        for tipo in TipoCompra:
            items = session_db.query(Item).filter_by(tipo_compra=tipo).all()
            data['tipos_compra_nombres'].append(tipo.value)
            data['tipos_compra_valores'].append(sum(i.valor_unitario * i.cantidad for i in items if i.valor_unitario))
            data['tipos_compra_cantidades_items'].append(sum(i.cantidad for i in items))

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session_db.close()

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

# Ejecutar app
if __name__ == '__main__':
    app.run(debug=True)
