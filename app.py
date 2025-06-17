from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, Column, String, Integer, Float, Enum as SQLAlchemyEnum
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm.exc import NoResultFound
import enum
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

Base = declarative_base()

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

engine = create_engine('sqlite:///inventario_web.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/', methods=['GET', 'POST'])
def index():
    session = Session()
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
            session.add(nuevo_item)
            session.commit()
            flash("Ítem agregado con éxito", "success")
        except Exception as e:
            session.rollback()
            flash(f"Error al agregar: {e}", "error")
        finally:
            session.close()
        return redirect(url_for('index'))

    items = session.query(Item).order_by(Item.nombre).all()
    session.close()
    return render_template('index.html', items=items, categorias=CategoriaItem, estados=EstadoItem, tipos_compra=TipoCompra)

@app.route('/editar/<item_id>', methods=['GET', 'POST'])
def editar(item_id):
    session = Session()
    item = session.query(Item).filter_by(id=item_id).first()
    if not item:
        session.close()
        flash("Ítem no encontrado", "error")
        return redirect(url_for('index'))

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
            session.commit()
            flash("Ítem actualizado correctamente", "success")
        except Exception as e:
            session.rollback()
            flash(f"Error al actualizar ítem: {e}", "error")
        finally:
            session.close()
        return redirect(url_for('index'))

    session.close()
    return render_template('editar.html', item=item, categorias=CategoriaItem, estados=EstadoItem, tipos_compra=TipoCompra)

@app.route('/eliminar/<item_id>', methods=['POST'])
def eliminar(item_id):
    session = Session()
    try:
        item = session.query(Item).filter_by(id=item_id).first()
        if item:
            session.delete(item)
            session.commit()
            flash("Ítem eliminado correctamente", "success")
        else:
            flash("Ítem no encontrado", "error")
    except Exception as e:
        session.rollback()
        flash(f"Error al eliminar ítem: {e}", "error")
    finally:
        session.close()
    return redirect(url_for('index'))

@app.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')

@app.route('/api/estadisticas')
def api_estadisticas():
    session = Session()
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
            items = session.query(Item).filter_by(categoria=cat).all()
            data['categorias_nombres'].append(cat.value)
            data['categorias_valores'].append(sum(i.valor_unitario * i.cantidad for i in items if i.valor_unitario))
            data['categorias_cantidades_items'].append(sum(i.cantidad for i in items))

        for est in EstadoItem:
            items = session.query(Item).filter_by(estado=est).all()
            data['estados_nombres'].append(est.value)
            data['estados_valores'].append(sum(i.valor_unitario * i.cantidad for i in items if i.valor_unitario))
            data['estados_cantidades_items'].append(sum(i.cantidad for i in items))

        for tipo in TipoCompra:
            items = session.query(Item).filter_by(tipo_compra=tipo).all()
            data['tipos_compra_nombres'].append(tipo.value)
            data['tipos_compra_valores'].append(sum(i.valor_unitario * i.cantidad for i in items if i.valor_unitario))
            data['tipos_compra_cantidades_items'].append(sum(i.cantidad for i in items))

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)
