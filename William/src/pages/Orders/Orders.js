import React from 'react';
import Paper from '@material-ui/core/Paper'
import Link from '@material-ui/core/Link';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

// Generate Order Data
function createData(id, date, name, shipTo, paymentMethod, amount) {
  return { id, date, name, shipTo, paymentMethod, amount };
}

const rows = [
  createData(0, '26 Aug, 2020', 'Bobby Orr', 'Parry Sound, Canada', 'VISA ⠀•••• 3719', 312.44),
  createData(1, '26 Aug, 2020', 'Ted Williams', 'San Diego, CA', 'VISA ⠀•••• 2574', 866.99),
  createData(4, '25 Aug, 2020', 'Bill Rodgers', 'Hartford, CT', 'VISA ⠀•••• 5919', 212.79),
  createData(2, '26 Aug, 2020', 'Larry Bird', 'West Springs, IN', 'MC ⠀•••• 1253', 100.81),
  createData(3, '26 Aug, 2020', 'Tom Brady', 'San Mateo, CA', 'AMEX ⠀•••• 2000', 654.39),
];

function preventDefault(event) {
  event.preventDefault();
}

const useStyles = makeStyles((theme) => ({
  seeMore: {
    marginTop: theme.spacing(3),
  },
}));

export default function Orders() {
  const classes = useStyles();
  return (
    <Paper>
      <h1>Recent Orders</h1>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Ship To</TableCell>
            <TableCell>Payment Method</TableCell>
            <TableCell align="right">Sale Amount</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell>{row.date}</TableCell>
              <TableCell>{row.name}</TableCell>
              <TableCell>{row.shipTo}</TableCell>
              <TableCell>{row.paymentMethod}</TableCell>
              <TableCell align="right">{row.amount}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <div className={classes.seeMore}>
        <Link color="primary" href="#" onClick={preventDefault}>
          See more orders
        </Link>
      </div>
    </Paper>
  );
}
