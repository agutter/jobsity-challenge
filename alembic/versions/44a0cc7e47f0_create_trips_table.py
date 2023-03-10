"""create trips table

Revision ID: 44a0cc7e47f0
Revises: 
Create Date: 2023-02-14 15:02:24.708543

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = '44a0cc7e47f0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('trips',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('region', sa.String(), nullable=False),
    sa.Column('origin_coord', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
    sa.Column('destination_coord', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('datasource', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_index('idx_trips_origin_coord', table_name='trips', postgresql_using='gist')
    op.drop_index('idx_trips_destination_coord', table_name='trips', postgresql_using='gist')
    op.create_index('idx_trips_destination_coord', 'trips', ['destination_coord'], unique=False, postgresql_using='gist')
    op.create_index('idx_trips_origin_coord', 'trips', ['origin_coord'], unique=False, postgresql_using='gist')
    #op.drop_table('spatial_ref_sys')
    #op.drop_table('layer')
    #op.drop_table('topology')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('topology',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('topology_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('precision', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('hasz', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='topology_pkey'),
    sa.UniqueConstraint('name', name='topology_name_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('layer',
    sa.Column('topology_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('layer_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('schema_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('table_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('feature_column', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('feature_type', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('level', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('child_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['topology_id'], ['topology.id'], name='layer_topology_id_fkey'),
    sa.PrimaryKeyConstraint('topology_id', 'layer_id', name='layer_pkey'),
    sa.UniqueConstraint('schema_name', 'table_name', 'feature_column', name='layer_schema_name_table_name_feature_column_key')
    )
    op.create_table('spatial_ref_sys',
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.CheckConstraint('srid > 0 AND srid <= 998999', name='spatial_ref_sys_srid_check'),
    sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    )
    op.drop_index('idx_trips_origin_coord', table_name='trips', postgresql_using='gist')
    op.drop_index('idx_trips_destination_coord', table_name='trips', postgresql_using='gist')
    op.drop_table('trips')
    # ### end Alembic commands ###
