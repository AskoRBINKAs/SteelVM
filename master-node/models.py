from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Model(DeclarativeBase):
    pass


class HostMachine(Model):
    __tablename__ = "hosts"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    access_key: Mapped[str]
    online: Mapped[bool] = mapped_column(default=False)
    ip_address: Mapped[str] = mapped_column(default='--')
    port: Mapped[int] = mapped_column(default=-1)
    cpu_count: Mapped[int] = mapped_column(default=0)
    ram_count: Mapped[int] = mapped_column(default=0)
    host_os: Mapped[str] = mapped_column(default='unknown')
    activated: Mapped[bool] = mapped_column(default=False)
    vm_type: Mapped[str]


class User(Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)