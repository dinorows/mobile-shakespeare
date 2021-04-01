import React from 'react';
import Paper from '@material-ui/core/Paper'
import Link from '@material-ui/core/Link';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

function preventDefault(event) {
  event.preventDefault();
}

const useStyles = makeStyles({
  depositContext: {
    flex: 1,
  },
});

export default function Deposits() {
  const classes = useStyles();
  return (
    <Paper>
      <h1>Recent Deposits</h1>
      <Typography component="p" variant="h4">
        $2,027.00
      </Typography>
      <Typography color="textSecondary" className={classes.depositContext}>
        on 26 August, 2020
      </Typography>
      <div>
        <Link color="primary" href="#" onClick={preventDefault}>
          View balance
        </Link>
      </div>
    </Paper>
  );
}
