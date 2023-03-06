export default function UserList(props) {
    return (
        <section style={{ "width": "25%", "position": "absolute", "right": 0, "border": "1px solid green", "height": "100%" }}>
            Users:
            <ul style={{ "textDecoration": "none", "listStyle": "none" }}>
                {
                    props.users.map((user) => {
                        if (user.name)
                            return (
                                <li key={user.id}>
                                    {user.name}
                                </li>
                            )
                        else
                            return (
                                <li key={user.id}>
                                    {user.first_name} {user.last_name}
                                </li>
                            )
                    })
                }
            </ul>
        </section>
    );
}