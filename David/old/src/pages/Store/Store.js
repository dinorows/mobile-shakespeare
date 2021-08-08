import React from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";
import GridList from "@material-ui/core/GridList";
import GridListTile from "@material-ui/core/GridListTile";

const styles = theme => ({
  root: {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "space-around",
    overflow: "hidden",
    backgroundColor: theme.palette.background.paper,
    marginTop: '100px'
  },
  gridList: {
    width: 500,
    height: 450
  },
  subheader: {
    width: "100%"
  }
});

const tileData = [
  {
    img: "https://material-ui.com/static/images/grid-list/breakfast.jpg",
    title: "Breakfast",
    author: "jill111",
    cols: 2,
    featured: true
  },
  {
    img: "https://material-ui.com/static/images/grid-list/burgers.jpg",
    title: "Tasty burger",
    author: "director90"
  },
  {
    img: "https://material-ui.com/static/images/grid-list/camera.jpg",
    title: "Camera",
    author: "Danson67"
  },
  {
    img: "https://material-ui.com/static/images/grid-list/morning.jpg",
    title: "Morning",
    author: "fancycrave1",
    featured: true
  },
  {
    img: "https://material-ui.com/static/images/grid-list/hats.jpg",
    title: "Hats",
    author: "Hans"
  },
  {
    img: "https://material-ui.com/static/images/grid-list/honey.jpg",
    title: "Honey",
    author: "fancycravel"
  },
  {
    img: "https://material-ui.com/static/images/grid-list/vegetables.jpg",
    title: "Vegetables",
    author: "jill111",
    cols: 2
  },
  {
    img: "https://material-ui.com/static/images/grid-list/plant.jpg",
    title: "Water plant",
    author: "BkrmadtyaKarki"
  },
  {
    img: "https://material-ui.com/static/images/grid-list/mushroom.jpg",
    title: "Mushrooms",
    author: "PublicDomainPictures"
  },
  {
    img: "https://material-ui.com/static/images/grid-list/olive.jpg",
    title: "Olive oil",
    author: "congerdesign"
  },
  {
    img: "https://material-ui.com/static/images/grid-list/star.jpg",
    title: "Sea star",
    cols: 2,
    author: "821292"
  },
  {
    img: "https://material-ui.com/static/images/grid-list/bike.jpg",
    title: "Bike",
    author: "danfador"
  }
];

function Store(props) {
  const { classes } = props;

  return (
      <div className={classes.root}>
        <GridList cellHeight={160} className={classes.gridList} cols={3}>
          {tileData.map(tile => (
            <GridListTile key={tile.img} cols={tile.cols || 1}>
              <img src={tile.img} alt={tile.title} />
            </GridListTile>
          ))}
        </GridList>
      </div>
  );
}

Store.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(styles)(Store);
